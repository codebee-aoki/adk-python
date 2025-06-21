# Human-in-the-Loop エージェント - 技術ドキュメント

## 概要

Human-in-the-Loop エージェント（`human_in_loop`）は、経費精算承認プロセスを通じて人間の介入が必要な長時間実行ツールの実装方法を実演するエージェントです。自動承認と管理者承認の判定ロジック、承認待ち状態の管理、非同期処理フローなど、実際のビジネスプロセスに即した Human-in-the-Loop パターンを学ぶことができます。

## 技術仕様

### アーキテクチャ

```python
# Human-in-the-Loop 対応エージェント
root_agent = Agent(
    model='gemini-1.5-flash',
    name='reimbursement_agent',
    instruction="...",  # 経費精算処理ロジック
    tools=[
        reimburse,                                    # 通常の精算ツール
        LongRunningFunctionTool(func=ask_for_approval)  # 長時間実行ツール
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
```

### 主要コンポーネント

#### 1. 経費精算ツール
```python
def reimburse(purpose: str, amount: float) -> str:
    """従業員への経費精算実行"""
    return {
        'status': 'ok',
    }
```

#### 2. 承認要求ツール（Long Running）
```python
def ask_for_approval(
    purpose: str, amount: float, tool_context: ToolContext
) -> dict[str, Any]:
    """管理者承認を要求（長時間実行）"""
    return {
        'status': 'pending',           # 待機状態
        'amount': amount,
        'ticketId': 'reimbursement-ticket-001',  # チケットID
    }
```

#### 3. LongRunningFunctionTool
```python
from google.adk.tools.long_running_tool import LongRunningFunctionTool

# 長時間実行ツールとしてラップ
LongRunningFunctionTool(func=ask_for_approval)
```

## 実行フロー

### 1. 自動承認フロー（金額 < $100）

```text
ユーザー入力: "タクシー代 $50 の精算をお願いします"

エージェント判断:
- 金額が $100 未満
- 自動承認対象

実行:
1. reimburse("タクシー代", 50.0) を直接呼び出し
2. {'status': 'ok'} を受信
3. 承認完了メッセージを返却

結果: 即座に精算完了
```

### 2. 管理者承認フロー（金額 >= $100）

```text
ユーザー入力: "出張費 $500 の精算をお願いします"

エージェント判断:
- 金額が $100 以上
- 管理者承認が必要

実行:
1. ask_for_approval("出張費", 500.0) を呼び出し
2. {'status': 'pending', 'ticketId': '...'} を受信
3. 承認待ち状態を通知

待機状態:
- チケット ID: reimbursement-ticket-001
- 管理者の承認待ち
- エージェントは一時停止

承認後:
- 管理者が承認 → reimburse() を実行
- 管理者が却下 → 却下理由を通知
```

## ビジネスロジック

### 承認ルール

```python
instruction = """
You are an agent whose job is to handle the reimbursement process for
the employees. If the amount is less than $100, you will automatically
approve the reimbursement.

If the amount is greater than $100, you will
ask for approval from the manager. If the manager approves, you will
call reimburse() to reimburse the amount to the employee. If the manager
rejects, you will inform the employee of the rejection.
"""
```

**決定フロー**:
1. **金額判定**: amount < $100 ? 自動承認 : 管理者承認
2. **自動承認**: `reimburse()` 直接実行
3. **管理者承認**: `ask_for_approval()` → 承認待ち → `reimburse()`
4. **却下処理**: 却下理由の通知

### 状態管理

**承認状態の追跡**:
```python
# 承認要求時の状態
{
    'status': 'pending',           # 承認待ち
    'amount': 500.0,              # 精算金額
    'ticketId': 'reimbursement-ticket-001',  # 追跡ID
    'purpose': '出張費',           # 用途
    'timestamp': '2025-01-01T10:00:00Z'  # 要求時刻
}
```

## 使用例

### 基本的な使用方法

**自動承認ケース**:
```python
response = await root_agent.invoke("昼食代 $25 の精算をお願いします")

# 期待される応答:
# "$25 の昼食代を自動承認し、精算処理を完了しました。"
```

**管理者承認ケース**:
```python
response = await root_agent.invoke("会議室レンタル $200 の精算をお願いします")

# 期待される応答:
# "$200 の会議室レンタル費は管理者承認が必要です。
# 承認チケット reimbursement-ticket-001 を発行しました。
# 管理者の承認をお待ちください。"
```

### 複雑なシナリオ

**複数精算の処理**:
```python
# 複数の精算要求
requests = [
    "交通費 $30",     # 自動承認
    "宿泊費 $150",    # 管理者承認
    "資料代 $45",     # 自動承認
]

for req in requests:
    response = await root_agent.invoke(f"{req} の精算をお願いします")
    # 各要求に応じて適切な処理フローを実行
```

## 高度な実装例

### 1. 承認チケット管理システム

```python
class ApprovalTicketManager:
    def __init__(self):
        self.tickets = {}
    
    def create_ticket(self, purpose: str, amount: float, employee_id: str):
        ticket_id = f"ticket-{len(self.tickets) + 1:03d}"
        self.tickets[ticket_id] = {
            'purpose': purpose,
            'amount': amount,
            'employee_id': employee_id,
            'status': 'pending',
            'created_at': datetime.now(),
        }
        return ticket_id
    
    def approve_ticket(self, ticket_id: str, manager_id: str):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]['status'] = 'approved'
            self.tickets[ticket_id]['approved_by'] = manager_id
            return True
        return False
```

### 2. 通知システム統合

```python
async def ask_for_approval_with_notification(
    purpose: str, amount: float, tool_context: ToolContext
):
    """承認要求 + 通知送信"""
    ticket_id = generate_ticket_id()
    
    # 管理者への通知送信
    await send_notification_to_manager(
        message=f"新しい精算承認要求: {purpose} ${amount}",
        ticket_id=ticket_id
    )
    
    # Slack/Teams への通知
    await send_slack_message(
        channel="#approvals",
        message=f"💰 精算承認要求\n用途: {purpose}\n金額: ${amount}\nチケット: {ticket_id}"
    )
    
    return {
        'status': 'pending',
        'amount': amount,
        'ticketId': ticket_id,
        'notification_sent': True
    }
```

### 3. 承認履歴とレポート

```python
class ReimbursementReporter:
    def generate_monthly_report(self, month: str):
        """月次精算レポート生成"""
        auto_approved = self.get_auto_approved_transactions(month)
        manager_approved = self.get_manager_approved_transactions(month)
        
        return {
            'month': month,
            'auto_approved_count': len(auto_approved),
            'auto_approved_total': sum(t['amount'] for t in auto_approved),
            'manager_approved_count': len(manager_approved),
            'manager_approved_total': sum(t['amount'] for t in manager_approved),
            'average_approval_time': self.calculate_avg_approval_time(manager_approved)
        }
```

## 実践的な応用例

### 1. 企業経費管理システム

```python
class CorporateExpenseSystem:
    def __init__(self):
        self.approval_rules = {
            'meals': {'limit': 50, 'requires_receipt': True},
            'travel': {'limit': 100, 'requires_booking_confirmation': True},
            'supplies': {'limit': 200, 'requires_purchase_order': False},
        }
    
    async def process_expense(self, category: str, amount: float, documents: list):
        rule = self.approval_rules.get(category)
        if not rule:
            return await self.request_manual_review(category, amount)
        
        if amount <= rule['limit']:
            if rule.get('requires_receipt') and not self.has_receipt(documents):
                return await self.request_receipt_upload()
            return await self.auto_approve(category, amount)
        else:
            return await self.request_manager_approval(category, amount, documents)
```

### 2. 多層承認システム

```python
class MultiTierApprovalSystem:
    def __init__(self):
        self.approval_tiers = [
            {'limit': 1000, 'approver': 'team_lead'},
            {'limit': 5000, 'approver': 'department_manager'},
            {'limit': 20000, 'approver': 'director'},
            {'limit': float('inf'), 'approver': 'ceo'},
        ]
    
    def get_required_approver(self, amount: float):
        for tier in self.approval_tiers:
            if amount <= tier['limit']:
                return tier['approver']
        return 'board_approval'
```

### 3. 条件分岐承認ロジック

```python
async def smart_approval_logic(purpose: str, amount: float, employee_data: dict):
    """高度な承認判定ロジック"""
    
    # 従業員の権限レベル確認
    if employee_data.get('level') == 'senior' and amount < 200:
        return await auto_approve(purpose, amount)
    
    # 定期的な経費の場合
    if is_recurring_expense(purpose) and amount < 150:
        return await auto_approve(purpose, amount)
    
    # 緊急度の確認
    if 'urgent' in purpose.lower() and amount < 500:
        return await expedited_approval(purpose, amount)
    
    # デフォルトの承認フロー
    return await standard_approval_flow(purpose, amount)
```

## 設定とカスタマイズ

### 温度設定
```python
# 一貫した判定のため低温度設定
generate_content_config=types.GenerateContentConfig(temperature=0.1)
```

### 承認閾値の設定
```python
# 環境変数での設定
APPROVAL_THRESHOLD = os.getenv('APPROVAL_THRESHOLD', 100)

# 動的設定
approval_threshold = get_department_approval_limit(employee_department)
```

## 技術的制約と考慮事項

### 1. 長時間実行ツールの制約
- ツール実行が完了するまでエージェントは待機
- タイムアウト設定の考慮が必要
- 状態の永続化と復旧機能

### 2. 非同期処理の考慮
- 承認待ち中の他のリクエスト処理
- 複数チケットの並列管理
- 承認結果の非同期通知

### 3. エラーハンドリング
- 承認タイムアウト
- 承認者不在時の処理
- システム障害時の復旧

## 関連ファイル

- `agent.py`: メインエージェント実装
- `main.py`: 実行エントリーポイント
- `README.md`: 英語版ドキュメント
- `README_ja.md`: 日本語版ドキュメント

## 依存関係

- `google.adk`: ADK フレームワーク
- `google.adk.tools.long_running_tool`: 長時間実行ツール
- `google.adk.tools`: ツールコンテキスト
- `google.genai.types`: Google AI タイプ定義
- `typing`: 型ヒント
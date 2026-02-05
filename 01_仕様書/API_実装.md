# 実装手順
## 1. DBモデル作成（SQLAlchemy）
models.pyを作る

## 2. 認証

## 3. listen_logs_API

## 4. discography API


## 必ずしたいチェック
- `PATCH/DELETE`で`log.user_id == current_user.user_id`を確認して、違えば`403`
- ソフト削除なら、一覧系はdeleted_at is nullを必ず条件に入れる

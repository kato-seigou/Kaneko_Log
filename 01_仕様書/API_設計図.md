# API設計書
## 概要
### 1) 認証（ユーザー登録・ログイン）
> ここはDBのCRUDより、認証APIとして必要な物だけ作る
- `POST /auth/register`：ユーザー登録
- `POST /auth/login`：ログインしてトークン発行？
- `POST /auth/logout`：ログアウト

### 2) ディスコグラフィ
> ユーザーは編集できないのでGETのみで可
- `GET /discographies`
- `GET /discographies/{id}`

### 3) 聞いた曲ログ
> ここが一番CRUDが効く
- `POST /listen-logs`: 記録する
- `PATCH /listen-logs/{log_id}`: ログを編集する
- `DELETE /listen-logs/{log_id}`: ログを削除する
- `GET /timeline`: 最新n件のタイムライン、ページング
- `GET /me/listen-logs`: 自分のログの取得

### 4) 統計
> 統計はDBのCRUDではなく、集計結果を返すAPIにする
- `GET /me/stats` 自分の統計

## 詳細
### 1) 認証系
#### `POST /auth/register`
- 目的: ユーザーの登録、パスワードの登録
- Auth: 不用
- Body: リクエストに送るデータ本体
    - `login_id: str`: ユーザーが指定（英数字記号10文字以内）（必須）
    - `password: str`: パスワード
- Response（201）
    - `login_id`:
    - `user_id`:
    - `created_at`:
- Errors:
    - 409: login_idにかぶりがある（Conflict）
    - 422: 文字数制限違反など

#### `POST /auth/login`
- 目的: ログインidとパスワードを入力してログイン
- Auth: 不用
- Body: 
    - `login_id: str`
    - `password: str`
- Response（200）: JWT方式でやる
    - `access_token: str`
    - `token_type: "bearer"`
- Errors:
    - `401 Unauthorized`: 資格情報が不正
    - `422 Unprocessable Entity`: 型・バリデーション違反（API由来）

#### `POST /auth/logout`（ここは後で考える）
- 目的: ログアウト
- Auth: 必要？
- Body:
    - `access_token`
- Response:
    - 特になしでいい？
    - `200 OK {"message": "logged out"}
- Errors:

### 2) ディスコグラフィ
#### `GET /discographies`
- 目的: 全てのディスコグラフィの取得
- Auth：不要
- Body:
    - これいるかな？
    - ただリクエストを送るだけでいいかも
    - なしで確定
        - 任意でQuery
            - `type: str`:  ジャンルで検索
            - `q: str`: タイトル検索
- Response（200）:
    - `discography_id`: DB側で自動的に降られた連番
    - `discography_title`: タイトル
    - `released_date`: リリース年月日
    - `discography_num`: 曲数
    - `discography_type`: アルバム、EP、シングルなのか
    - `playtime_seconds`: フル再生時間（秒）
    - `created_at`: DBへの登録年月日
- Errors:
    - `500` サーバーエラー
    - 基本無し

#### `GET /discographies/{id}`
一旦保留

### 3) 聞いた曲ログ
#### `POST /listen-logs`
- 目的: 聞いたディスコグラフィの記録を行う
- Auth: 必要
- Body:
    - `discography_id: int`
        - これをUI側では`discography_title`表示で、裏では`discography_id`を取得させて処理させたい
    - `comment: Optional[str]`
        - 50文字以内のコメント（感想とか・メモ用）
    - `listened_datetime: Optional[datetime.datetime]`
        - ディスコグラフィを聞いた時間
        - 未指定なら`now()`を取得
- Response（201）
    - `log_id`: logのID
    - `discography_id`
    - `comment`
    - `listened_datetime`
- Error
    - `401 Unauthorized`: 未ログイン
    - `404 Not Found`: `discography_id`が存在しない
    - `422 Unprocessable Entity`: commentが長い・方がおかしい
    - `409 Conflict`: 最短間隔ルール違反
        - まあ、いったんこれはあとでで

#### `GET /timeline`: 最新n件のタイムライン、ページング
- 目的: タイムラインの取得
- Auth: 必要
- Query: 
    - `limit: Optional[int]`
        - デフォルト: 50
        - 最大: 100
    - `before: Optional[datetime]`
        - 指定された時刻よりも前のログを取得
- Response（200）:
    - [
        {
            `log_id`: int,
            `discography_id`: int,
            `comment`: Optional[str],
            `listened_datetime`: datetime,
            `discography_title`: int
            `（任意）display_name`: str
        },
        ...
    ]
- Errors:
    - `422 Unprocessable Entity`: クエリの型不正
    - `401 Unauthorized`: 未ログイン

#### `GET /me/listen-logs`: 自分のログの取得
`/me/`はauthからuserを特定できる
- 目的: 自分の過去のログの取得
- Auth: 必要
- Query:
    - limit: Optional[int] 
        - default: limit=50, max=200
    - before: Optional[datetime]
- Response（200）:
    - [
        {
            log_id: int,
            discography_id: int,
            discography_title: str,
            comment: Optional[str],
            listened_datetime: datetime
        },
        ...
    ]
- Errors:
    - `401`: 未ログイン
    - `422`: 不正ログイン

#### `DELETE /listen-logs/{log_id}`: ログを削除する
- 目的: 自分のログの削除
- Auth: 必要（Bearer token）
- Path:
  - log_id: int
- Query:
    - `log_id: int`
- Response（200）
    - {"message": "Deleted"}
    - {"log_id": ..., "deleted_at": ...}
- 削除方式
    - ソフト削除
        - データに`deleted`みたいなのをつける
- Error:
    - `401 Unauthorized`: 未ログイン/トークン不正
    - `403 Forbidden`: 他人のログで削除不可
    - `403 Not Found`: `log_id`が存在しない

#### `PATCH /listen-logs/{log_id}`: ログを編集する
- 目的: 自分のログを編集する
- Auth: 必要（Bearer token）
- Path: APIのURLの中で「どのリソースを操作するか」を指定する部分
  - log_id: int
- Query:
    - `log_id: int`
- Body:
    - `commit`: Optional[str]
        - 50文字以内
    - `listened_datetime`: datetime[str]
        - 視聴日時の編集
        - 未指定の項目は変更しない
- Response（200）
    - `log_id`: int
    - `discography_id`: int
    - `comment`: Optional[str]
    - `listened_at`: datetime
- Errors:
    - `401 Unauthorized`: 未ログイン・トークン不正
    - `403 Forbidden`: 他人のログのため編集不可
    - `404 Not Found`: log_idが存在しない
    - `422 Unprocessable Entity`: バリデーション違反（comment長すぎなど）
# twiblo
ついったーまとめてブロック君

## とは
idが','で区切られているリスト形式のテキストファイルを与えると、対象idのユーザー全てをブロックする。

ただし下記条件のidはブロックしない。

- 対象idのユーザーを自分がフォローしている
- 対象idのユーザーからフォローされている
- 曲がりなりにも `verified` である

## どうやって

### うごかす
事前準備として

1. API Key
1. API Key Secret
1. Access Token
1. Access Token Secret
1. カンマ区切りでTwitter IDが連結しているテキストファイル

を用意し、かつ

- 自分がフォローしている人の全員のidがカンマ区切りで連結しているテキスト

と

- 自分をフォローしている人の全員のidがカンマ区切りで連結しているテキスト

の2つをハードコードすること。

### うごく
適当なとこから叩く

## なぜ
ヤバそうなアカウントをフォローしているやつらをまとめてブロックリストにぶち込むために作った。

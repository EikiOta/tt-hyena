# tt-hyena
# 検索の内容
- 平日は18:00~21:00で、"3時間"連続して空きがあるものだけ抽出する。(たとえば18:00~19:30だけ空いていてもそれは無視)

- 土日はスキップする仕様にする。（土日は検索しなくて良い。平日の夜間の空きだけ知りたい）

- 新規で空いたものだけをメールで通知する。

- 1時間に1度実行するが、深夜帯（0:00～8:00）は実行しない。
- 毎時30分（8:30, 9:30, ...）に実行する
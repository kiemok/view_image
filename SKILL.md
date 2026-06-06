---
name: view_image
description: 璇嗗埆鍥剧墖鍐呭骞朵互姝や负鍩虹鍥炵瓟鐢ㄦ埛鐨勯棶棰?runAs: subagent
allowed-tools: bash, read_file, glob, ls
---

# view_image 鈥?璇嗗埆鍥剧墖鍐呭骞跺洖绛旈棶棰?
浣犳槸鍥剧墖璇嗗埆鍔╂墜銆傜敤鎴烽€氳繃 arguments 浼犲叆鍥剧墖璺緞鍜屽彲鑳界殑鎻愰棶銆?
## Step 1: 鑷姩鍒嗙鎻愰棶鍜岃矾寰?
arguments 鍙兘鍖呭惈鎻愰棶鏂囧瓧锛屼篃鍙兘鍙湁璺緞銆傜敤浠ヤ笅閫昏緫鑷姩瑙ｆ瀽锛?
```powershell
$argsStr = "$arguments"

# 鎵惧埌 @ 鎴栫粷瀵硅矾寰勶紙鍚啋鍙风殑璺緞濡?C:/ 鎴?D:/锛?if ($argsStr -match '(@\S+|"@[^"]+")') {
    $imageToken = $matches[1] -replace '"', ''
    # @ 鍓嶉潰鐨勬墍鏈夋枃瀛楀氨鏄彁闂?    $question = ($argsStr -replace $matches[0], '').Trim()
} elseif ($argsStr -match '([A-Za-z]:\\[^ ]+)') {
    $imageToken = $matches[1]
    $question = ($argsStr -replace $matches[0], '').Trim()
} elseif ($argsStr -match '([A-Za-z]:/[^ ]+)') {
    $imageToken = $matches[1]
    $question = ($argsStr -replace $matches[0], '').Trim()
} else {
    $imageToken = $argsStr.Trim()
    $question = $null
}
```

鏈€缁堝緱鍒帮細
- `$imageToken` = 鍥剧墖璺緞鏍囪锛堝 `@image.png` 鎴?`C:\path\img.png`锛?- `$question` = 鐢ㄦ埛閽堝鍥剧墖鎻愮殑闂锛堝彲鑳戒负绌猴級

## Step 2: 瑙ｆ瀽鍥剧墖璺緞

濡傛灉 `$imageToken` 浠?`@` 寮€澶达紝鍓嶉潰鍔犱笂椤圭洰宸ヤ綔鐩綍锛?PWD锛夊緱鍒板畬鏁磋矾寰勩€?濡傛灉 `Test-Path` 涓嶅瓨鍦ㄥ垯鎶ュ憡閿欒銆?
## Step 3: 杩愯绋嬪簭璇嗗埆鍥剧墖

鍏堣缂栫爜閬垮厤 GBK 鏃犳硶鎵撳嵃 emoji/涓枃锛屽啀鎵ц銆?濡傛灉鐢ㄦ埛鏈夋彁闂紙`$question`锛夛紝鐢?`-p` 鍙傛暟浼犵粰鑴氭湰锛涘鏋滄病鏈夛紝涓嶅姞 `-p`锛?
```powershell
cd "$env:USERPROFILE\.reasonix\skills\view_image"
$env:PYTHONIOENCODING='utf-8'
# 鏈夋彁闂椂
python image_recognizer.py "<瀹屾暣璺緞>" -p "$question"
# 鏃犳彁闂椂
python image_recognizer.py "<瀹屾暣璺緞>"
```

鎹曡幏 stdout + stderr銆?
## Step 4: 鎻愬彇缁撴灉骞跺洖绛旂敤鎴?
绋嬪簭杈撳嚭涓?--- 涔嬮棿鐨勬枃瀛楀氨鏄浘鐗囨弿杩般€?
缁撳悎鍥剧墖鎻忚堪鍥炵瓟鐢ㄦ埛鐨勬彁闂細
- 濡傛灉鐢ㄦ埛闂簡闂锛堝"杩欐槸浠€涔堢綉椤?锛夛紝鐩存帴鐢ㄥ浘鐗囧唴瀹瑰洖绛?- 濡傛灉鐢ㄦ埛娌￠棶闂锛岀洿鎺ヤ粙缁嶅浘鐗囧唴瀹?
涓嶈璇?鎴戣繍琛屼簡绋嬪簭"鎴?绋嬪簭杈撳嚭鏄?杩欑被璇濄€傚氨鍍忎綘鑷繁鐪嬪埌鍥剧墖涓€鏍疯嚜鐒跺洖绛斻€?

#!/usr/bin/env bash
# Quét nhanh một website để gợi ý mức độ audit (xem references/00-triage.md).
#
#   scripts/scan.sh [thư-mục-code]       quét source code website hoặc mobile app (mặc định: thư mục hiện tại)
#   scripts/scan.sh https://ten-mien.vn  quét site đang chạy, khi không có source code
#
# Với thư mục: chỉ đọc file, không gọi mạng.
# Với URL: gọi scripts/fetch-site.sh để tải các trang công khai của chính site đó
# (trang chủ, trang chính sách/liên hệ/giỏ hàng, file JS cùng tên miền) về thư mục tạm,
# rồi quét như source code. Không gửi dữ liệu đi đâu khác.
#
# Kết quả là GỢI Ý kèm bằng chứng (file:dòng:đoạn khớp). Agent vẫn phải xem lại
# bằng chứng trước khi kết luận.

set -uo pipefail

TARGET="${1:-.}"
URL_MODE=0
if [[ "$TARGET" =~ ^https?:// ]]; then
  URL_MODE=1
  DIR="$(mktemp -d)"
  bash "$(dirname "$0")/fetch-site.sh" "$TARGET" "$DIR" || exit 1
  echo
else
  DIR="$TARGET"
  if [ ! -d "$DIR" ]; then
    echo "Không tìm thấy thư mục: $DIR" >&2
    exit 1
  fi
fi

# Chỉ quét file code/cấu hình, bỏ qua thư viện, build output, lockfile và chính bộ checklist
EXCLUDE_DIRS=(node_modules .git dist build out .next .nuxt .svelte-kit vendor coverage .vn-law-check
              .turbo Pods .dart_tool .gradle DerivedData .expo)
INCLUDE=(--include='*.html' --include='*.htm' --include='*.js' --include='*.mjs' --include='*.cjs'
         --include='*.jsx' --include='*.ts' --include='*.tsx' --include='*.vue' --include='*.svelte'
         --include='*.astro' --include='*.php' --include='*.py' --include='*.rb' --include='*.erb'
         --include='*.liquid' --include='*.twig' --include='*.json' --include='*.toml'
         --include='*.yml' --include='*.yaml' --include='*.env.example'
         --include='*.dart' --include='*.kt' --include='*.kts' --include='*.java' --include='*.swift'
         --include='*.m' --include='*.mm' --include='*.gradle' --include='AndroidManifest.xml'
         --include='Info.plist' --include='Podfile')

# -o: chỉ in đoạn khớp, để bằng chứng vẫn đọc được với file JS đã minify (cả file nằm trên 1 dòng)
GREP_ARGS=(-rEIino "${INCLUDE[@]}" --exclude='package-lock.json' --exclude='pnpm-lock.yaml' --exclude='yarn.lock' --exclude='*.lock' --exclude='*.min.js')
for d in "${EXCLUDE_DIRS[@]}"; do GREP_ARGS+=(--exclude-dir="$d"); done

# Mỗi tín hiệu: tên | regex. Có thêm mẫu cho JSX đã compile (jsx("form", createElement("form")
# vì site React/Next chỉ lộ form trong file JS.
SIGNALS=(
  "FORM|<form[ >]|jsxs?\(\"form\"|createElement\(\"form\"|formspree\.io|getform\.io|data-netlify=|docs\.google\.com/forms|type=[\"']email[\"']|type:[[:space:]]*[\"']email[\"']|keyboardType=[\"'](email-address|phone-pad)[\"']|textContentType=[\"'](emailAddress|telephoneNumber)[\"']|TextInputType\.(emailAddress|phone)"
  "TRACKING|gtag\(|googletagmanager\.com|google-analytics\.com|fbq\(|connect\.facebook\.net|analytics\.tiktok\.com|clarity\.ms|hotjar|cdn\.segment\.com|plausible\.io|umami"
  "COMMERCE|add[-_ ]?to[-_ ]?cart|addToCart|/(cart|checkout)([\"'/]|\.[a-z]+)|giỏ hàng|thêm vào giỏ|mua ngay|thanh toán|vnpay|momo|zalopay|\"stripe\"|stripe\.com|paypal|woocommerce"
  "AUTH|/login|/register|/signin|/signup|sign[-_ ]?in|đăng nhập|next-auth|nextauth|firebase/auth|supabase\.auth|passport|@clerk|auth0"
  "MARKETPLACE|multi[-_ ]?vendor|seller[-_ ]?(dashboard|register|signup|onboard)|vendor[-_ ]?(dashboard|register)|người bán|kênh người bán|đăng ký bán hàng"
  "AI|api\.openai\.com|\"openai\"|@anthropic-ai|api\.anthropic\.com|@ai-sdk|generativelanguage\.googleapis|@google/generative-ai|dialogflow|langchain|chatbot"
  "PERMISSIONS|android\.permission\.(ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|ACCESS_BACKGROUND_LOCATION|READ_CONTACTS|WRITE_CONTACTS|CAMERA|RECORD_AUDIO|READ_SMS|RECEIVE_SMS|READ_CALL_LOG|READ_PHONE_STATE|READ_MEDIA_IMAGES|READ_MEDIA_VIDEO|READ_EXTERNAL_STORAGE|BODY_SENSORS|ACTIVITY_RECOGNITION)|NS(LocationWhenInUse|LocationAlways|LocationAlwaysAndWhenInUse|Contacts|Camera|Microphone|PhotoLibrary|PhotoLibraryAdd|UserTracking|HealthShare|HealthUpdate|SpeechRecognition|Motion)UsageDescription|\"(ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|ACCESS_BACKGROUND_LOCATION|READ_CONTACTS|CAMERA|RECORD_AUDIO|READ_SMS)\""
  "SDK_TRACKING|firebase_analytics|@react-native-firebase/analytics|firebase-analytics|FirebaseAnalytics|react-native-fbsdk|facebook_app_events|FBSDKCoreKit|com\.facebook\.android|appsflyer|react-native-adjust|com\.adjust\.sdk|adjust_sdk|react-native-branch|io\.branch|mixpanel|amplitude|@segment/analytics-react-native|AppTrackingTransparency|app_tracking_transparency|react-native-tracking-transparency"
  "ADS_SDK|google_mobile_ads|react-native-google-mobile-ads|play-services-ads|Google-Mobile-Ads-SDK|GoogleMobileAds|applovin|unity-ads|unity_ads|ironsource|admob"
  "FOREIGN_HOST|amazonaws\.com|cloudfront\.net|firebaseio\.com|firebase\.json|\"firebase\"|firebase/firestore|vercel|netlify|wrangler|cloudflare|herokuapp|fly\.io|render\.com|azurewebsites"
)

# Dùng biến FOUND_<TÊN> thay cho mảng kết hợp, vì macOS mặc định là bash 3.2 (không có declare -A)
found() { local v="FOUND_$1"; [ "${!v:-0}" = 1 ]; }

echo "Quét: $([ "$URL_MODE" = 1 ] && echo "$TARGET" || echo "$DIR")"
echo

for entry in "${SIGNALS[@]}"; do
  name="${entry%%|*}"
  regex="${entry#*|}"
  limit=3; [ "$name" = PERMISSIONS ] && limit=10
  hits="$(grep "${GREP_ARGS[@]}" -e "$regex" "$DIR" 2>/dev/null | awk '!seen[$0]++' | head -n "$limit")"
  if [ "$name" = "FOREIGN_HOST" ] && [ -z "$hits" ]; then
    # Source code: nhận diện qua file cấu hình hosting
    hits="$(find "$DIR" -maxdepth 2 \( -name vercel.json -o -name netlify.toml -o -name firebase.json \
             -o -name wrangler.toml -o -name fly.toml -o -name render.yaml -o -name app.yaml \) 2>/dev/null | head -n 3)"
    # URL: nhận diện qua response header của trang chủ
    if [ -z "$hits" ] && [ -f "$DIR/response-headers.txt" ]; then
      hits="$(grep -iE '^(server|via|x-vercel-id|cf-ray|x-amz-cf-id|x-nf-request-id|x-served-by|x-github-request-id|x-powered-by):.*' "$DIR/response-headers.txt" \
              | grep -iE 'vercel|cloudflare|cf-ray|cloudfront|amazon|netlify|firebase|github|fly|render|heroku|azure|google' \
              | tr -d '\r' | sed 's/^/response-headers: /' | head -n 3)"
    fi
  fi
  if [ -n "$hits" ]; then
    printf -v "FOUND_$name" 1
    echo "[có]    $name"
    echo "$hits" | sed "s#^$DIR/##" | cut -c1-160 | sed 's/^/          /'
  else
    echo "[không] $name"
  fi
done

# Nhận diện mobile app qua file đặc trưng của từng nền tảng
platforms=""
if [ "$URL_MODE" = 0 ]; then
  has() { [ -n "$(find "$DIR" \( -name node_modules -o -name Pods -o -name .dart_tool -o -name .git \) -prune -o "$@" -print 2>/dev/null | head -n 1)" ]; }
  has -name pubspec.yaml && platforms="$platforms Flutter"
  has -name package.json -exec grep -q '"react-native"' {} \; && platforms="$platforms React-Native"
  has -name package.json -exec grep -q '"expo"' {} \; && platforms="$platforms Expo"
  has -name AndroidManifest.xml && platforms="$platforms Android"
  { has -name Info.plist || has -name '*.xcodeproj'; } && platforms="$platforms iOS"
fi
platforms="${platforms# }"

if [ -n "$platforms" ]; then
  echo "[có]    MOBILE_APP"
  echo "          $platforms"
  # Chức năng xóa tài khoản chỉ cần kiểm tra khi app có đăng nhập
  if found AUTH; then
    del="$(grep "${GREP_ARGS[@]}" -e 'delete[-_ ]?account|deleteAccount|deleteUser|xóa tài khoản|xoá tài khoản|account[-_ ]deletion' "$DIR" 2>/dev/null | head -n 2)"
    if [ -n "$del" ]; then
      echo "[có]    ACCOUNT_DELETE"
      echo "$del" | sed "s#^$DIR/##" | cut -c1-160 | sed 's/^/          /'
    else
      echo "[không] ACCOUNT_DELETE   (app có đăng nhập nhưng không thấy chức năng xóa tài khoản, xem 09 mục C)"
    fi
  fi
else
  echo "[không] MOBILE_APP"
fi

# Gợi ý mức theo bảng trong references/00-triage.md
if found AUTH && found MARKETPLACE; then
  level=3; desc="nền tảng/SaaS quy mô. Áp dụng toàn bộ 01-08"
elif found COMMERCE; then
  level=2; desc="bán hàng/TMĐT. Áp dụng 01 + 02 + 04 (thêm 05/06 nếu có quảng cáo, hợp đồng điện tử)"
elif found FORM || found TRACKING || found AUTH || found AI || found PERMISSIONS || found SDK_TRACKING || found ADS_SDK; then
  # Chatbot AI nhận tin nhắn tự do của người dùng và gửi tới bên thứ ba → coi như có thu thập dữ liệu
  level=1; desc="thu thập nhẹ. Áp dụng 01 mục A, B, C"
else
  level=0; desc="tĩnh hoàn toàn. Không cần audit chi tiết"
fi

ai="no";   found AI && ai="yes"
host="no"; found FOREIGN_HOST && host="yes"
app="no";  [ -n "$platforms" ] && app="yes"

echo
echo "Gợi ý: mức $level, $desc"
[ "$ai" = yes ]   && echo "        + có dấu hiệu AI → thêm 07-ai-transparency"
[ "$app" = yes ]  && echo "        + là mobile app ($platforms) → thêm 09-mobile-app"
# Site mức 0 không lưu dữ liệu cá nhân nên nhúng CDN/host nước ngoài không phát sinh nghĩa vụ chuyển dữ liệu
[ "$host" = yes ] && [ "$level" -ge 1 ] && echo "        + có dấu hiệu host/dịch vụ nước ngoài → xem 01 mục D nếu có lưu dữ liệu cá nhân"
if [ "$URL_MODE" = 1 ]; then
  echo
  echo "Các trang đã tải nằm ở: $DIR"
  echo "Đọc trang chính sách trong pages/ để audit nội dung."
  echo "Quét qua URL không thấy được code phía server (chatbot gọi AI qua server, nơi lưu dữ liệu),"
  echo "nên cần xem thêm trực tiếp trên trang, ví dụ có khung chat nào không."
fi
echo
echo "LEVEL=$level AI=$ai FOREIGN_HOST=$host APP=$app"

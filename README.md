# Auto Comment Tool - Multi-Platform Social Media Automation
auto_comment_tool/
├── main.py                 # Entry point
├── account_manager.py      # Quản lý tài khoản
├── proxy_manager.py        # Xử lý proxy
├── comment_engine.py       # Logic comment
├── scheduler.py            # Điều chỉnh thời gian
├── web_dashboard.py        # Giao diện web
├── utils.py                # Hàm hỗ trợ
├── requirements.txt        # Dependencies
├── .env.example            # Environment variables
├── config.json             # Configuration
└── README.md               # Hướng dẫn

## 📌 Giới thiệu

Tool tự động bình luận cho các nền tảng mạng xã hội Facebook, TikTok, Instagram với giao diện quản lý web, hỗ trợ nhiều tài khoản, proxy riêng và cơ chế anti-detect.

## ✨ Tính năng chính

- ✅ Quản lý nhiều tài khoản (thêm/sửa/xóa)
- ✅ Proxy riêng cho từng tài khoản (HTTP/HTTPS/SOCKS5)
- ✅ Tự động bình luận với nội dung random
- ✅ Điều chỉnh thời gian linh hoạt
- ✅ Giao diện web dashboard quản lý
- ✅ Cơ chế anti-detect và xử lý lỗi

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- Chrome browser (cho Selenium)
- pip (Python package manager)

### Các bước cài đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd auto_comment_tool

# Triển khai dự án Website vinhvu.xyz lên VPS (ubuntu)

## Phần chuẩn bị
- Mua Vps hệ ubuntu bản thấp nhất 20.04 trở lên
- Đăng ký 1 tên miền chính chủ vinhvu.xyz từ các bên cho thuê.
- Vào DNS tên miền đã thuê và trỏ ip VPS đã mua.

## Phần kết nối VPS để tiến hành triển khai dự án
- Có thể tải phần mềm Bitvise trên trình duyệt , sau đó tiến hành đăng nhập vào VPS

## Phần 1: Cài đặt các gói cần thiết trên VPS đã mua
Trước khi đi sâu vào cài đặt các gói cần thiết, chúng ta cần cập nhật và nâng cấp máy chủ cũng như các gói hiện có lên phiên bản mới nhất.
```bash
sudo apt update -y
sudo apt upgrade -y
```

Cài đặt tất cả các gói cần thiết trong một lệnh.
```bash
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl file
```

Danh sách các gói được cài đặt là:
Pip (trình cài đặt gói Python)
Tập tin phát triển Python
PostgreSQL và Thư viện
Máy chủ web Nginx

## Phần 2: Tạo người dùng và cơ sở dữ liệu Postgres trong VPS
Chạy lệnh sau để vào môi trường Postgres. Theo mặc định khi Postgres được cài đặt, chúng tôi sẽ có một người dùng tên là 'postgres' có quyền quản trị trong PostgreSQL. Chúng tôi sử dụng người dùng này để tạo Cơ sở dữ liệu và tài khoản Người dùng trong postgres cho dự án của chúng tôi.
```bash
sudo -u postgres psql
```

Tạo cơ sở dữ liệu cho dự án của chúng tôi
```bash
CREATE DATABASE ducads;
```

Lưu ý:  Mọi câu lệnh Postgres PHẢI kết thúc bằng dấu chấm phẩy

Tạo người dùng cơ sở dữ liệu cho dự án của chúng tôi. Đảm bảo chọn mật khẩu an toàn.
```bash
CREATE USER postgres WITH PASSWORD 'admin';
```
ALTER USER postgres WITH PASSWORD 'admin';

Lưu ý: Người dùng cơ sở dữ liệu ở đây là 'postgres' và mật khẩu là 'admin'

Đặt mã hóa mặc định thành UTF-8, được Django khuyên dùng
```bash
ALTER ROLE postgres SET client_encoding TO 'utf8';
```

Đặt sơ đồ cách ly giao dịch mặc định thành 'đọc đã cam kết'. Điều này chặn việc đọc từ các giao dịch không được cam kết.
```bash
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
```

Đặt múi giờ mặc định thành UTC. Đây là múi giờ mặc định mà dự án Django của chúng tôi cũng sẽ có.
```bash
ALTER ROLE postgres SET timezone TO 'UTC';
```

Bây giờ, hãy cung cấp cho người dùng cơ sở dữ liệu của chúng tôi 'postgres' để có tất cả các đặc quyền trong cơ sở dữ liệu 'Restoran' .
```bash
GRANT ALL PRIVILEGES ON DATABASE Restoran TO postgres;
```

Bây giờ chúng tôi đã tạo thành công cơ sở dữ liệu và người dùng cơ sở dữ liệu có tất cả các đặc quyền đối với cơ sở dữ liệu mà chúng tôi đã tạo trong PostgreSQL. Thoát khỏi môi trường Postgres.
```bash
\q
```

## Phần 3: Tạo môi trường ảo Python
Nâng cấp pip và cài đặt môi trường ảo Python.
```bash
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
```

Tạo một thư mục dự án nơi bạn có thể tạo môi trường ảo và cài đặt django, gunicorn, v.v. cho dự án của chúng tôi. Trong hướng dẫn này, tôi sẽ tạo thư mục dự án bên trong thư mục /home/ .
```bash
cd /home
mkdir sleekproject
```

Điều hướng đến thư mục/thư mục dự án.
```bash
cd sleekproject/
```

Tạo môi trường ảo bên trong thư mục dự án. Tôi đặt tên môi trường virut là 'sleekenv' .
```bash
virtualenv sleekenv
```

Điều này sẽ tạo một thư mục có tên  ' sleekenv'  trong thư mục ' sleekproject'  . Bên trong, nó sẽ cài đặt phiên bản cục bộ của Python và phiên bản cục bộ của  pip. Chúng ta có thể sử dụng điều này để cài đặt và định cấu hình môi trường Python riêng biệt cho dự án của mình. Trước khi cài đặt các yêu cầu Python của dự án, chúng ta cần kích hoạt môi trường ảo.
```bash
source sleekenv/bin/activate
```

Dấu nhắc đầu cuối sẽ thay đổi để cho biết rằng bạn hiện đang hoạt động trong môi trường ảo Python. Nó sẽ trông giống như thế này
(sleekenv) root@host:/home/sleekproject#

Khi môi trường ảo được kích hoạt, giờ đây chúng ta có thể cài đặt Django, Gunicorn và bộ điều hợp PostgreSQL (psycopg2) bằng pip. Trong môi trường ảo, chúng ta chỉ có thể sử dụng pip thay vì pip3 bất kể bạn có đang sử dụng Python phiên bản 3 hay không.
```bash
pip install django gunicorn psycopg2-binary pillow
pip install django-environ django-tailwind django-browser-reload django-ckeditor requests

```


Bây giờ chúng tôi có tất cả phần mềm cần thiết để bắt đầu dự án Django.

## Phần 4: Tạo và cấu hình dự án Website
Dấu nhắc đầu cuối:
(sleekenv) root@host:/home/sleekproject#

Clone dự án github về thư mục:
```bash
git clone https://github.com/thaisung/vinh_vu_wix.git
```

Tiêp theo di chuyển vào thu mục sleeksoft:
```bash
cd sleeksoft/
```

Áp dụng các thay dổi xuống cơ sở dữ liệu:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Bây giờ, hãy tạo một siêu người dùng cho trang web của chúng tôi.
```bash
python3 manage.py createsuperuser
```

Bạn nên nhập tên người dùng, email và mật khẩu để tạo tài khoản superuser. Sau này, hãy thực hiện lệnh collstatic sẽ thu thập tất cả các tệp tĩnh trong trang web của chúng tôi vào thư mục /static/. Hãy nhớ rằng chúng ta đã xác định thư mục '/static/' trong settings.py.
```bash
python3 manage.py collectstatic
```

Tạo một ngoại lệ cho cổng 8000. Vì vậy, chúng tôi có thể kiểm tra xem thiết lập Django đã được cài đặt đúng cách chưa.
```bash
sudo ufw allow 8000
```

Bây giờ, chúng tôi có thể kiểm tra dự án của mình bằng cách khởi động máy chủ phát triển Django bằng lệnh sau
```bash
python3 manage.py runserver 0.0.0.0:8000
```

Trong trình duyệt web, hãy truy cập tên miền hoặc địa chỉ IP của máy chủ, sau đó là  :8000. Ở đây 8000 là số cổng.
http://server_domain_or_IP:8000

Liên kết Gunicorn với dự án của chúng tôi
Chạy lệnh sau để liên kết Gunicorn với dự án của chúng tôi.
```bash
gunicorn --bind 0.0.0.0:8000 sleeksoft.wsgi
```

Điều này sẽ khởi động Gunicorn trên cùng giao diện mà máy chủ phát triển Django đang chạy. Chúng ta có thể quay lại và kiểm tra lại trang web. Sự khác biệt duy nhất là chúng tôi không thực hiện lệnh startserver từ Django, thay vào đó Gunicorn sẽ đảm nhiệm việc đó.
Lưu ý:  Trong một số trường hợp, giao diện quản trị sẽ không được áp dụng bất kỳ kiểu dáng nào vì Gunicorn không biết cách tìm nội dung CSS tĩnh chịu trách nhiệm cho việc này. Chúng tôi sẽ cấu hình nó trong Nginx.
Sau khi kiểm tra xong, hãy sử dụng CTRL-C  trong cửa sổ terminal để dừng Gunicorn. Bây giờ chúng ta đã hoàn tất việc định cấu hình ứng dụng / Trang web Django của mình. Chúng ta có thể thoát khỏi môi trường ảo bằng lệnh sau.
```bash
deactivate
```
Chỉ báo môi trường ảo trong dấu nhắc lệnh sẽ bị xóa.

## Phần 5: Tạo các tập tin dịch vụ và socket systemd cho Gunicorn
Chúng tôi đã kiểm tra rằng Gunicorn có thể tương tác với ứng dụng Django của chúng tôi, nhưng chúng tôi nên triển khai một cách dễ dàng và hiệu quả để khởi động và dừng máy chủ ứng dụng. Để đạt được điều này, chúng tôi sẽ tạo các tệp ổ cắm và dịch vụ systemd cho Gunicorn.
Tạo và mở tệp socket systemd cho Gunicorn theo đường dẫn sau.
```bash
sudo touch /etc/systemd/system/gunicorn.socket
```

Tệp gunicorn.socket sẽ được tạo theo đường dẫn trên, tải xuống qua FTP và bắt đầu thêm đoạn mã sau vào nó:
```bash
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Lưu, đóng và tải tệp lên qua FTP khi bạn hoàn tất.
Tiếp theo, tạo và mở tệp dịch vụ systemd cho Gunicorn với đặc quyền sudo. Tên tệp dịch vụ phải khớp với tên tệp ổ cắm ngoại trừ phần mở rộng:
```bash
sudo touch /etc/systemd/system/gunicorn.service
```
Tệp gunicorn.service sẽ được tạo theo đường dẫn trên, tải xuống qua FTP và bắt đầu thêm đoạn mã sau vào nó.:
```bash
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/home/sleekproject/sleeksoft

ExecStart=/home/sleekproject/sleekenv/bin/gunicorn \
    --workers 3 \
    --threads 2 \
    --bind unix:/run/gunicorn.sock \
    --access-logfile - \
    --error-logfile - \
    sleeksoft.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Lưu, đóng và tải tệp lên qua FTP khi bạn hoàn tất.
Bây giờ, tệp dịch vụ systemd của chúng tôi đã hoàn tất. Bây giờ chúng ta có thể bắt đầu và kích hoạt ổ cắm Gunicorn. Điều này sẽ tạo tệp ổ cắm tại /run/gunicorn.sock ngay bây giờ và khi khởi động. Khi kết nối được thực hiện với ổ cắm đó, systemd sẽ tự động khởi động gunicorn.service để xử lý nó.
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

Chúng tôi có thể xác nhận rằng thao tác đã thành công bằng cách kiểm tra tệp ổ cắm. Kiểm tra trạng thái của quá trình để tìm hiểu xem nó có thể bắt đầu hay không:
```bash
sudo systemctl status gunicorn.socket
```

Tiếp theo, kiểm tra sự tồn tại của file gunicorn.sock trong thư mục /run
```bash
file /run/gunicorn.sock
```
Đầu ra: /run/gunicorn.sock: socket

Nếu lệnh trạng thái systemctl hiển thị lỗi hoặc nếu bạn không tìm thấy tệp gunicorn.sock trong thư mục, đó là dấu hiệu cho thấy ổ cắm Gunicorn không thể được tạo chính xác. Kiểm tra nhật ký của ổ cắm Gunicorn bằng lệnh sau
```bash
sudo journalctl -u gunicorn.socket
```

Kiểm tra kích hoạt ổ cắm
Hiện tại, chúng tôi đã khởi động đơn vị gunicorn.socket, gunicorn.service sẽ chưa hoạt động vì socket chưa nhận được bất kỳ kết nối nào. chúng ta có thể kiểm tra điều này bằng cách sử dụng lệnh sau
```bash
sudo systemctl status gunicorn
```
Đầu ra:

● gunicorn.service - gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
   Active: inactive (dead)

Để kiểm tra kích hoạt ổ cắm, chúng ta có thể gửi kết nối đến ổ cắm thông qua cuộn tròn bằng cách sử dụng lệnh sau
```bash
curl --unix-socket /run/gunicorn.sock localhost
```

Bạn sẽ thấy đầu ra HTML từ ứng dụng django của chúng tôi trong thiết bị đầu cuối. Điều này có nghĩa là Gunicorn đã được khởi động và có thể phục vụ ứng dụng Django của chúng tôi. Chúng tôi có thể xác minh rằng dịch vụ Gunicorn đang chạy bằng cách sử dụng lệnh sau
```bash
sudo systemctl status gunicorn
```

Đầu ra:

gunicorn.service - gunicorn daemon
    Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
    Active: active (running) since Mon 2021-05-10 21:00:35 UTC; 4s ago
  Main PID: 1157 (gunicorn)
     Tasks: 4 (limit: 1153)
    CGroup: /system.slice/gunicorn.service
            ├─1157 /home/sleekproject/sleekenv/bin/python3 /home/sleekproject/sleekenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock sleeksoft.wsgi:application
            ├─1178 /home/sleekproject/sleekenv/bin/python3 /home/sleekproject/sleekenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock sleeksoft.wsgi:application
            ├─1180 /home/sleekproject/sleekenv/bin/python3 /home/sleekproject/sleekenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock sleeksoft.wsgi:application
            └─1181 /home/sleekproject/sleekenv/bin/python3 /home/sleekproject/sleekenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock sleeksoft.wsgi:application
 May 10 21:00:35 django1 systemd[1]: Started gunicorn daemon.
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1157] [INFO] Starting gunicorn 19.9.0
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1157] [INFO] Listening at: unix:/run/gunicorn.sock (1157)
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1157] [INFO] Using worker: sync
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1178] [INFO] Booting worker with pid: 1178
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1180] [INFO] Booting worker with pid: 1180
 May 10 21:00:35 django1 gunicorn[1157]: [2018-07-09 20:00:40 +0000] [1181] [INFO] Booting worker with pid: 1181
 May 10 21:00:36 django1 gunicorn[1157]:  - - [10/May/2021:21:00:36 +0000] "GET / HTTP/1.1" 200 16348 "-" "curl/7.58.0"
Nếu đầu ra từ Curl hoặc đầu ra của systemctl status cho biết đã xảy ra sự cố, hãy kiểm tra nhật ký để biết thêm chi tiết:

sudo journalctl -u gunicorn
Kiểm tra tệp /etc/systemd/system/gunicorn.service xem có vấn đề gì không. Nếu chúng tôi thực hiện các thay đổi đối với tệp /etc/systemd/system/gunicorn.service , hãy tải lại daemon để đọc lại định nghĩa dịch vụ và khởi động lại quy trình Gunicorn bằng lệnh sau
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

## Phần 6: Cấu hình máy chủ web Nginx
Chúng ta cần định cấu hình Nginx để chuyển lưu lượng truy cập đến quy trình Gunicorn. Chúng ta cần tạo và mở một khối máy chủ mới trong thư mục có sẵn trên các trang của Nginx bằng lệnh sau.
```bash
sudo touch /etc/nginx/sites-available/sleeksoft
```

Tải tập tin này qua FTP và bắt đầu chỉnh sửa. Chúng tôi sẽ thêm phần sau vào khối máy chủ này.
Chỉ định rằng khối này sẽ lắng nghe trên cổng 80 bình thường và nó sẽ phản hồi với tên miền hoặc địa chỉ IP của máy chủ của chúng tôi.
Hướng dẫn Nginx bỏ qua mọi vấn đề khi tìm favicon.
Hướng dẫn Nginx về nơi tìm các tệp tĩnh mà chúng tôi đã thu thập trong  /sleekproject/static thư mục của mình. Tất cả các tệp này đều có tiền tố URI tiêu chuẩn là “/static”, vì vậy chúng tôi có thể tạo một khối vị trí để khớp với các yêu cầu đó

```bash
server {
    server_name vinhvu.xyz;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/sleekproject/sleeksoft/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Lưu, đóng và tải tệp lên qua FTP khi bạn hoàn tất. Bây giờ, chúng ta có thể kích hoạt tệp bằng cách liên kết nó với thư mục hỗ trợ trang web
```bash
sudo ln -s /etc/nginx/sites-available/sleeksoft /etc/nginx/sites-enabled
```

Kiểm tra cấu hình Nginx để tìm lỗi cú pháp bằng cách sử dụng lệnh sau
```bash
sudo nginx -t
```

Nếu không có lỗi nào được báo cáo thì chúng ta có thể tiếp tục và khởi động lại Nginx bằng cách sử dụng lệnh sau
```bash
sudo systemctl restart nginx
```

Bây giờ, chúng tôi cần mở tường lửa của mình cho lưu lượng truy cập bình thường trên cổng 80. Vì chúng tôi không cần quyền truy cập vào máy chủ phát triển nữa nên chúng tôi có thể xóa quy tắc mở cổng 8000 ngay bây giờ.
```bash
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

Bây giờ chúng ta có thể truy cập miền hoặc địa chỉ IP của máy chủ để xem ứng dụng/trang web Django của chúng ta.

## Phần 7: Cài đặt Certbot để kích hoạt SSL
cài đặt snapd
```bash
sudo apt install snapd
```

Thực hiện các hướng dẫn sau trên dòng lệnh trên máy để đảm bảo rằng bạn có phiên bản snapd mới nhất
```bash
sudo snap install core; sudo snap refresh core
```

Chạy lệnh này trên dòng lệnh trên máy để cài đặt Certbot.
```bash
sudo snap install --classic certbot
```

Thực hiện hướng dẫn sau trên dòng lệnh trên máy để đảm bảo rằng lệnh certbot có thể chạy được.
```bash
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Chạy lệnh này để nhận chứng chỉ và để Certbot tự động chỉnh sửa cấu hình Nginx của bạn để phục vụ nó, bật quyền truy cập HTTPS chỉ trong một bước.
```bash
sudo certbot --nginx
```

Khi được nhắc, hãy nhập giá trị mong muốn. Điều này sẽ tự động tạo chứng chỉ SSL cho tên miền trỏ.

Bây giờ khởi động lại máy chủ.
```bash
reboot
```
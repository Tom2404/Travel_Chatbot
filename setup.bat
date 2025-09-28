@echo off
echo ===============================================
echo KHOI TAO DU AN TRAVEL CHATBOT
echo ===============================================

echo.
echo [1] Cai dat dependencies...
pip install -r requirements.txt

echo.
echo [2] Tao migration cho models...
python manage.py makemigrations

echo.
echo [3] Chay migration...
python manage.py migrate

echo.
echo [4] Thu thap static files...
python manage.py collectstatic --noinput

echo.
echo [5] Tao superuser (nhap thong tin neu can)...
python manage.py createsuperuser

echo.
echo ===============================================
echo KHOI TAO HOAN THANH!
echo ===============================================
echo.
echo Chay lenh sau de khoi dong server:
echo python manage.py runserver
echo.
echo Truy cap:
echo - Website: http://127.0.0.1:8000/
echo - Admin: http://127.0.0.1:8000/admin/
echo.
pause
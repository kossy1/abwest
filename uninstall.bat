@echo off
echo 🧹 Uninstalling large packages...

pip uninstall -y torch torchvision torchaudio
pip uninstall -y tensorflow
pip uninstall -y transformers
pip uninstall -y numpy
pip uninstall -y scikit-learn
pip uninstall -y pandas
pip uninstall -y scipy
pip uninstall -y matplotlib
pip uninstall -y seaborn
pip uninstall -y jupyter

pip uninstall -y gunicorn
pip uninstall -y uvicorn
pip uninstall -y celery
pip uninstall -y redis
pip uninstall -y django-debug-toolbar
pip uninstall -y django-allauth
pip uninstall -y djongo
pip uninstall -y mongoengine

echo ✅ Cleanup complete!
pause
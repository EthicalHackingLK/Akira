if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/sahanhisharasl/xandria.git /xandria
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /xandria
fi
cd /xandria
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py

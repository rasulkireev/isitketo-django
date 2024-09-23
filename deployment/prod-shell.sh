ssh -t root@138.201.126.181 'docker exec -it $(docker ps --filter "name=srv-captain--isitketo" | grep "^.*srv-captain--isitketo\." | awk '\''{print $1}'\'') python manage.py shell_plus --ipython'

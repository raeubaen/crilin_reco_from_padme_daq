import os 
import subprocess
import time

process =0
workdir = "/Users/elisadimeco/OnlineMonitor/"

while True:
    print("coping new fragment")
    os.system(f"sshpass -p mu2e scp mu2e@mu2edaq:/home/mu2e/onlinemonitor/outonline/onlinemonitorbtf_last_summary.root  {workdir}.")

    if process != 0:
        print("killing")
        process.communicate(input=b'.q')
    process = subprocess.Popen(["root", "-l", "-x", f"plot_client_btf.C()"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(30)

if [ -f "/home/aiida/.ssh/config" ]; then
    cat /home/aiida/apps/aiidalab-mp-uc3/sshfiles/config >> /home/aiida/.ssh/config
else
    cp /home/aiida/apps/aiidalab-mp-uc3/sshfiles/config /home/aiida/.ssh/
fi

# I'm certain smarter use of options would mean we can bypass copying the known_hosts
# AiiDA's AutoAdd policy *should* handle this, but doesn't...
if [ -f "/home/aiida/.ssh/known_hosts" ]; then
    cat /home/aiida/apps/aiidalab-mp-uc3/sshfiles/known_hosts >> /home/aiida/.ssh/known_hosts
else
    cp /home/aiida/apps/aiidalab-mp-uc3/sshfiles/known_hosts /home/aiida/.ssh/
fi

verdi computer setup --config /home/aiida/apps/aiidalab-mp-uc3/setup_files/unity/computer_setup.yml
verdi computer configure ssh --config /home/aiida/apps/aiidalab-mp-uc3/setup_files/unity/computer_configure.yml unity
verdi code setup --config /home/aiida/apps/aiidalab-mp-uc3/setup_files/unity/code_setup.yml

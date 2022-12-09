if [ -f "/home/aiida/.ssh/config" ]; then
    cat /home/aiida/apps/mp-uc3/sshfiles/config >> /home/aiida/.ssh/config
else
    cp /home/aiida/apps/mp-uc3/sshfiles/config /home/aiida/.ssh/
fi

# I'm certain smarter use of options would mean we can bypass copying the known_hosts
# AiiDA's AutoAdd policy *should* handle this, but doesn't...
if [ -f "/home/aiida/.ssh/known_hosts" ]; then
    cat /home/aiida/apps/mp-uc3/sshfiles/known_hosts >> /home/aiida/.ssh/known_hosts
else
    cp /home/aiida/apps/mp-uc3/sshfiles/known_hosts /home/aiida/.ssh/
fi

verdi computer setup --config /home/aiida/apps/mp-uc3/setup_files/droplet/computer_setup.yml
verdi computer configure ssh --config /home/aiida/apps/mp-uc3/setup_files/droplet/computer_configure.yml droplet
verdi code setup --config /home/aiida/apps/mp-uc3/setup_files/droplet/code_setup.yml

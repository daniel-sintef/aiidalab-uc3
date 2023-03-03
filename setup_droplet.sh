USER=jovyan
ROOT=$(dirname $(realpath "$0"))

if [ -f "/home/${USER}/.ssh/config" ]; then
    cat $ROOT/sshfiles/config >> /home/$USER/.ssh/config
else
    cp $ROOT/sshfiles/config /home/$USER/.ssh/
fi

# I'm certain smarter use of options would mean we can bypass copying the known_hosts
# $USER's AutoAdd policy *should* handle this, but doesn't...
if [ -f "/home/${USER}/.ssh/known_hosts" ]; then
    cat $ROOT/sshfiles/known_hosts >> /home/$USER/.ssh/known_hosts
else
    cp $ROOT/sshfiles/known_hosts /home/$USER/.ssh/
fi

verdi computer setup -n --config $ROOT/setup_files/droplet/computer_setup.yml
verdi computer configure core.ssh -n --config $ROOT/setup_files/droplet/computer_configure.yml droplet
verdi code create core.code.installed -n --config  $ROOT/setup_files/droplet/code_setup.yml

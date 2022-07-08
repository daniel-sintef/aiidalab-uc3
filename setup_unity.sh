cp ./sshfiles/stepstone /home/aiida/.ssh/
cp ./sshfiles/config /home/aiida/.ssh/

# I'm certain smarter use of options would mean we can bypass copyin gthe known_hosts
# AiiDA's AutoAdd policy *should* handle this, but doesn't...
cp ./sshfiles/known_hosts /home/aiida/.ssh/

verdi computer setup --config ./setup_files/unity/computer_setup.yml
verdi computer configure ssh --config ./setup_files/unity/computer_configure.yml unity
verdi code setup --config ./setup_files/unity/code_setup.yml

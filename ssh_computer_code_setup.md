# SSH Computer Code setup

1. Start the ssh agent [local computer]

      $eval $(ssh-agent -s)

2. Copy my ssh key to ./sshfiles/stepstone

3. Start the aiidalab docker instance

4. From the aiidalab comamnd line run the setup script

      $sh /home/aiida/apps/aiidalab-mp-uc3/setup_unity.sh

5. Activate the UC3 app and run, the app, with FSP@unity

**) I gave up on using ProxyJump was getting several different errors and (~2 hours effort)

1. raise valueerror("q must be exactly 160, 224, or 256 bits long") valueerror: q must be exactly 160, 224, or 256 bits long
   Bypassed by creating ed25519 key
2. disconnect (code 2 received packet inappropriate for current authentication state)
   No clue about this one
3. paramiko.ssh_exception.ChannelException: ChannelException(1, 'Administratively prohibited')
   No clue about this one

Meanwhile proxycommand worked with almost no effort... (~10 minutes)

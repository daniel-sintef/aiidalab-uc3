FROM aiidalab/aiidalab-docker-stack:latest

RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

# Setup Computer and Code
# RUN ssh-add /run/secrets/sintef_ssh_key \
#     && ssh-add /run/secrets/mp_gitlab_ssh_key
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan gitlab.cc-asp.fraunhofer.de >> ~/.ssh/known_hosts
# RUN --mount=type=secret,id=mp_gitlab_ssh_key eval $(ssh-agent -s) && ssh-add /run/secrets/mp_gitlab_ssh_key
# RUN echo "HOST gitlab.cc-asp.fraunhofer.de\n  HostName gitlab.cc-asp.fraunhofer.de\n  User git\n  IdentityFile /run/secrets/mp_gitlab_ssh_key" >> ~/.ssh/config
# RUN cat ~/.ssh/config && exit 1
RUN git config --global user.name "Casper Welzel Andersen" && git config --global user.email "casper.w.andersen@sintef.no"
# RUN --mount=type=secret,id=mp_gitlab_ssh_key git clone git@gitlab.cc-asp.fraunhofer.de:Daniel.Marchand/aiida-marketusercase3.git
RUN mkdir -p /marketplace
RUN --mount=type=ssh git clone git@gitlab.cc-asp.fraunhofer.de:Daniel.Marchand/aiida-marketusercase3.git /marketplace/aiida-marketusercase3

ENV AIIDALAB_DEFAULT_APPS "aiidalab-widgets-base@https://github.com/aiidalab/aiidalab-widgets-base@v1.3.3"

# Copy in UC3 App
COPY *.py *.ipynb LICENSE *.md *.txt *.cfg ${AIIDALAB_APPS}/aiidalab-mp-uc3/
COPY img ${AIIDALAB_APPS}/aiidalab-mp-uc3/img

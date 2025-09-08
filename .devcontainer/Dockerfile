FROM alpine
ARG S6_OVERLAY_VERSION=3.2.1.0

RUN <<EOT
	apk upgrade --no-cache
	apk add --no-cache bash nix shadow xz
EOT

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
COPY s6 /etc/s6-overlay/s6-rc.d

RUN <<EOT
	cat <<EOF >>/etc/nix/nix.conf &&
experimental-features = nix-command flakes
trusted-users = root vscode
EOF
	useradd -mU vscode -G nix -s /bin/bash
EOT
ENV PATH="/nix/var/nix/profiles/default/bin:/nix/var/nix/profiles/default/sbin:$PATH"

USER vscode
RUN <<EOT
	mkdir -p ~/.config/direnv
	cat <<EOF > ~/.config/direnv/config.toml
[whitelist]
prefix = [ '/workspaces' ]
EOF
EOT

USER root
ENTRYPOINT ["/init"]
CMD ["/bin/sleep", "inf"]

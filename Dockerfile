FROM bitnami/kubectl:1.20.9 as kubectl

FROM ubuntu:22.04


# Do whatever you need to with the
# ubuntu-or-whatever-image:tag image, then:

COPY --from=kubectl /opt/bitnami/kubectl/bin/kubectl /usr/local/bin/

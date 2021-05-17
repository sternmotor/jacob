Rancher


Infrastructure: 
* loadbalancer in front of controlplane/etcd servers 
	* https://rancher.com/docs/rancher/v2.x/en/installation/other-installation-methods/behind-proxy/prepare-nodes/
* loadbalancer with fixed, permanent URL for access from workers/ other clusters (public fqdn)
* 3x controlplane server: 2x RZ, 1x GS,  4GB RAM, 4 CPUs


Install simple:
* https://www.der-bode.de/search/rancher
	* RKE installation
	* Node setup (sysctl stuff) 
* https://rancher.com/docs/rke/latest/en/example-yamls/

Requirements

* Hardware: 
	* https://rancher.com/docs/rancher/v2.x/en/installation/requirements/
* general requirements https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#ensure-iptables-tooling-does-not-use-the-nftables-backend
* CentOS8 for hosts, letsencrypt for public access
	* Basic stuff
		

		sudo yum install iptables
		sudo yum install container-selinux
		yum install -y arptables.x86_64 ebtables.x86_64 nscd.x86_64 iptables.x86_64 nftables.x86_64 conntrack-tools.x86_64
		systemctl start nscd nftables
		systemctl enable nscd nftables
	* Hardening- ! not tested!

		cat << EOF > /etc/sysctl.d/90-kubelet.conf
		vm.overcommit_memory=1
		vm.panic_on_oom=0
		kernel.panic=10
		kernel.panic_on_oops=1
		kernel.keys.root_maxbytes=25000000
		EOF
		sysctl -p /etc/sysctl.d/90-kubelet.conf

	* let iptables see bridged traffic

		cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
		net.bridge.bridge-nf-call-ip6tables = 1
		net.bridge.bridge-nf-call-iptables = 1
		EOF
		sudo sysctl --system

	* install modules

		cat <<EOF | sudo tee /etc/modules-load.d/rke.conf
		ip6_udp_tunnel
		ip_set
		ip_set_hash_ip
		ip_set_hash_net
		iptable_mangle
		iptable_raw
		nf_conntrack
		veth
		vxlan
		xt_comment
		xt_mark
		xt_multiport
		xt_nat
		xt_recent
		xt_set
		xt_statistic
		xt_tcpudp
		nf_conntrack
		EOF
		for i in $(cat /etc/modules-load.d/rke.conf); do 
		    modprobe $i
		done

	* RKE user - ? LDAP auth?, admin user?

		useradd -m -G docker rke
		passwd rke 
		su - rke
		mkdir $HOME/.ssh
		chmod 700 $HOME/.ssh
		touch $HOME/.ssh/authorized_keys
		echo "PLEASE PUT YOUR SSH KEY HERE" >> /home/rke/.ssh/authorized_keys

	* control plane servers

		groupadd --gid 52034 etcd
		useradd --comment "etcd service account" --uid 52034 --gid 52034 etcd


Ports used:

* https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#ensure-iptables-tooling-does-not-use-the-nftables-backend

# For etcd nodes, run the following commands:
firewall-cmd --permanent --add-port=2376/tcp
firewall-cmd --permanent --add-port=2379/tcp
firewall-cmd --permanent --add-port=2380/tcp
firewall-cmd --permanent --add-port=8472/udp
firewall-cmd --permanent --add-port=9099/tcp
firewall-cmd --permanent --add-port=10250/tcp

# For control plane nodes, run the following commands:
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=2376/tcp
firewall-cmd --permanent --add-port=6443/tcp
firewall-cmd --permanent --add-port=8472/udp
firewall-cmd --permanent --add-port=9099/tcp
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --permanent --add-port=10254/tcp
firewall-cmd --permanent --add-port=30000-32767/tcp
firewall-cmd --permanent --add-port=30000-32767/udp

# For worker nodes, run the following commands:
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=2376/tcp
firewall-cmd --permanent --add-port=8472/udp
firewall-cmd --permanent --add-port=9099/tcp
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --permanent --add-port=10254/tcp
firewall-cmd --permanent --add-port=30000-32767/tcp
firewall-cmd --permanent --add-port=30000-32767/udp
firewall-cmd --reload


Terms:

* kubeadm: the command to bootstrap the cluster.
* kubelet: the component that runs on all of the machines in your cluster and does things like starting pods and containers.
* kubectl: the command line util to talk to your cluster.

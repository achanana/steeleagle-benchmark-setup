VPN_IF="wg0"
VPN_SERV="cloudlet033.elijah.cs.cmu.edu"
VPN_PORT="51820"
INTERFACE="10.6.6"
VPN_ADDR="${INTERFACE}.2/24"

if [ ! -f "wgserver.key" ] && [ ! -f "wgserver.pub" ]; then
	wg genkey | tee wgserver.key | wg pubkey > wgserver.pub
else
	echo "Not generating server key: aleady exists"
fi
if [ ! -f "wgclient.key" ] && [ ! -f "wgclient.pub" ]; then
	wg genkey | tee wgclient.key | wg pubkey > wgclient.pub
else
	echo "Not generating client key: already exists"
fi
if [ ! -f "wgclient.psk" ]; then
	wg genpsk > wgclient.psk
else
	echo "Not generating shared secret: already exists"
fi

# Client private key
VPN_KEY="$(cat wgclient.key)"
 
# Pre-shared key
VPN_PSK="$(cat wgclient.psk)"
 
# Server public key
VPN_PUB="$(cat wgserver.pub)"

# Configure firewall
uci rename firewall.@zone[0]="lan"
uci rename firewall.@zone[1]="wan"
uci del_list firewall.wan.network="lte"
uci add_list firewall.wan.network="lte"

rule_name='drone_to_vpn_redirect'
uci -q delete firewall.$rule_name
uci batch << EOI
set firewall.$rule_name=redirect
set firewall.$rule_name.dest='vpn'
set firewall.$rule_name.dest_ip='10.6.6.1'
set firewall.$rule_name.dest_port='55004'
set firewall.$rule_name.src='drone'
set firewall.$rule_name.src_dport='55004'
set firewall.$rule_name.proto='udp'
set firewall.$rule_name.target='DNAT'
set firewall.$rule_name.name='DNAT drone to vpn for udp traffic'
EOI

name='vpn_zone'
uci -q delete firewall.$name
uci batch << EOI
set firewall.$name=zone
set firewall.$name.output='ACCEPT'
set firewall.$name.input='ACCEPT'
set firewall.$name.forward='ACCEPT'
set firewall.$name.network='${VPN_IF}'
set firewall.$name.name='vpn'
EOI

name='drone_zone'
uci -q delete firewall.$name
uci batch << EOI
set firewall.$name=zone
set firewall.$name.output='ACCEPT'
set firewall.$name.input='ACCEPT'
set firewall.$name.forward='ACCEPT'
set firewall.$name.network='wwan'
set firewall.$name.name='drone'
EOI

rule_name='vpn_to_drone_rule'
uci -q delete firewall.$rule_name
uci batch << EOI
set firewall.$rule_name=rule
set firewall.$rule_name.dest='drone'
set firewall.$rule_name.src='vpn'
set firewall.$rule_name.proto='all'
set firewall.$rule_name.target='ACCEPT'
set firewall.$rule_name.name='Allow vpn to drone zone'
EOI

uci commit firewall
echo -en "\nRestarting firewall... "
/etc/init.d/firewall restart >/dev/null 2>&1
echo "Done"

# Configure network
uci -q delete network.${VPN_IF}
uci set network.${VPN_IF}="interface"
uci set network.${VPN_IF}.proto="wireguard"
uci set network.${VPN_IF}.private_key="${VPN_KEY}"
uci add_list network.${VPN_IF}.addresses="${VPN_ADDR}"

# Add VPN peers
uci -q delete network.wgserver
uci set network.wgserver="wireguard_${VPN_IF}"
uci set network.wgserver.public_key="${VPN_PUB}"
uci set network.wgserver.preshared_key="${VPN_PSK}"
uci set network.wgserver.endpoint_host="${VPN_SERV}"
uci set network.wgserver.endpoint_port="${VPN_PORT}"
uci set network.wgserver.persistent_keepalive="25"
uci set network.wgserver.route_allowed_ips="1"
uci add_list network.wgserver.allowed_ips="${INTERFACE}.1/32"

uci commit network

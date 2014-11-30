PUBLIC_IF=eth0 # network card to apply the QoS to
LAN_IF=eth1 # network card to apply the QoS to
UPLINK=5000 # upload in kbits/s
DOWNLINK=100000 # download in kbits/s
TC=/usr/bin/tc
IPT=/usr/bin/iptables
case "$1" in
    start)
        echo "~~~~ LOADING $PUBLIC_IF TRAFFIC CONTROL RULES FOR `uname -n` ~~~~"
        echo
        echo "#-cleanup"
        $TC qdisc del dev $PUBLIC_IF root
        $IPT -t mangle -F

        # burst = rate * expected ping

        # the r2q value is calculated to let ~3 full packets pass before
        # rescheduling, so r2q = (UPLINK / (3 * MTU * 8))
        echo "#-define a HTB root qdisc"
        $TC qdisc add dev $PUBLIC_IF root handle 1: htb default 999

        # this is the main branch that sets the total bandwidth available to the leaves
        echo "#--uplink - rate $UPLINK kbit ceil $UPLINK kbit"
        $TC class add dev $PUBLIC_IF parent 1:0 classid 1:1 htb \
            rate $(($UPLINK))kbit ceil $(($UPLINK))kbit

        # INTERACTIVE CLASS: for low latency, high priority packets such as VoIP and DNS
        # it has little bandwidth assigned to it, but pass before everything else
        rate=$(( $UPLINK * 10 / 100 ))
        ceil=$(( $UPLINK * 80 / 100 ))
        echo "#---interactive - id 100 - rate $rate kbit ceil $ceil kbit"
        $TC class add dev $PUBLIC_IF parent 1:1 classid 1:100 htb \
            rate ${rate}kbit ceil ${ceil}kbit \
            burst $(( $rate * 20 / 1000 ))k cburst $(($ceil * 10/1000))k prio 1
        # this class transmits uses a pfifo before exiting
        echo "#--- ~ sub interactive: pfifo"
        $TC qdisc add dev $PUBLIC_IF parent 1:100 handle 1100: pfifo
        # filter definition, that will catch all the packets carrying the mark 100
        echo "#--- ~ interactive filter"
        $TC filter add dev $PUBLIC_IF parent 1:0 protocol ip prio 1 \
            handle 100 fw flowid 1:100
        # netfilter/iptables rules, will mark all UDP packets
        echo "#--- ~ netfilter rule - all UDP traffic at 100"
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p udp -j CONNMARK --set-mark 100
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p icmp -j CONNMARK --set-mark 100

        # TCP ACKs class: it's important to let the ACKs leave the network as fast as possible
        # when a host of the network is downloading.
        rate=$(( $UPLINK * 7 / 10 ))
        ceil=$(( $UPLINK ))
        echo "#---tcp acks - id 200 - rate $rate kbit ceil $ceil kbit"
        $TC class add dev $PUBLIC_IF parent 1:1 classid 1:200 htb \
            rate ${rate}kbit ceil ${ceil}kbit burst $(($rate * 30/1000)) prio 2
        echo "#--- ~ sub tcp acks: sfq"
        $TC qdisc add dev $PUBLIC_IF parent 1:200 handle 1200: sfq perturb 10 limit 32
        echo "#--- ~ filtre tcp acks"
        $TC filter add dev $PUBLIC_IF parent 1:0 protocol ip prio 2 handle 200 fw flowid 1:200
        echo "#--- ~ netfilter rule for TCP ACKs will be loaded at the end"

        # SSH class: for outgoing connections to avoid lag when somebody else is downloading
        # however, an SSH connection cannot fill up the connection to more than 70%
        echo "#---ssh - id 300 - rate $(( $UPLINK * 0.1 )) kbit ceil $(( $UPLINK * 0.9 )) kbit"
        $TC class add dev $PUBLIC_IF parent 1:1 classid 1:300 htb \
            rate $(( $UPLINK * 0.1 ))kbit ceil $(( $UPLINK * 0.9 ))kbit burst 15k prio 3
        # SFQ will mix the packets if there are several SSH connections in parallel
        # and ensure that none has the priority
        echo "#--- ~ sub ssh: sfq"
        $TC qdisc add dev $PUBLIC_IF parent 1:300 handle 1300: sfq perturb 10
        echo "#--- ~ ssh filter"
        $TC filter add dev $PUBLIC_IF parent 1:0 protocol ip prio 3 handle 300 fw flowid 1:300
        echo "#--- ~ netfilter rule - SSH at 300"
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p tcp --tcp-flags SYN SYN \
            --dport 22 -j CONNMARK --set-mark 300

        # HTTP class: All web browsing (80/443) gets half the bandwidth and can borrow full
        echo "#---http branch - id 400 - rate $(( $UPLINK * 0.2 )) kbit ceil $UPLINK kbit"
        $TC class add dev $PUBLIC_IF parent 1:1 classid 1:400 htb \
            rate $(( $UPLINK * 0.2 ))kbit ceil $(( $UPLINK ))kbit burst 30k prio 4
        echo "#--- ~ sub http branch: sfq"
        $TC qdisc add dev $PUBLIC_IF parent 1:400 handle 1400: sfq perturb 10
        echo "#--- ~ http branch filter"
        $TC filter add dev $PUBLIC_IF parent 1:0 protocol ip prio 4 handle 400 fw flowid 1:400
        echo "#--- ~ netfilter rule - http/s"
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p tcp --tcp-flags SYN SYN \
            --dport 80 -j CONNMARK --set-mark 400
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p tcp --tcp-flags SYN SYN \
            --dport 443 -j CONNMARK --set-mark 400

        # DEFAULT Class: the root qdisc will send all non filtered traffic to this one
        # we also set a netfilter rule to send large file transfert to this queue
        # and avoid impacting the HTTP queue
        rate=$(( $UPLINK * 80 / 100 ))
        ceil=$(( $UPLINK ))
        echo "#---default - id 999 - rate ${rate}kbit ceil ${ceil}kbit"
        $TC class add dev $PUBLIC_IF parent 1:1 classid 1:999 htb \
            rate ${rate}kbit ceil ${ceil}kbit burst $((rate * 40/1000)) prio 9
        echo "#--- ~ sub default: sfq"
        $TC qdisc add dev $PUBLIC_IF parent 1:999 handle 1999: sfq perturb 10
        echo "#--- ~ filtre default"
        $TC filter add dev $PUBLIC_IF parent 1:0 protocol ip prio 99 handle 999 fw flowid 1:999
        $IPT -t mangle -A POSTROUTING -o $PUBLIC_IF -p tcp -m connbytes --connbytes 10000000: \
            --connbytes-mode bytes --connbytes-dir both -j CONNMARK --set-mark 999
        echo "#--- ~ propagating marks on connections"
        $IPT -t mangle -A POSTROUTING -j CONNMARK --restore-mark
        echo "#--- ~ Mark TCP ACKs flags at 200"
        $IPT -t mangle -A POSTROUTING -p tcp --tcp-flags URG,ACK,PSH,RST,SYN,FIN ACK \
            -m length --length 40:64 -j MARK --set-mark 200
        echo
        echo "Traffic Control is up and running"
        echo
        ;;
    stop)
        $IPT -t mangle -F
        $IPT -t mangle -X
        echo "iptables rules removed"
        $TC qdisc del dev $PUBLIC_IF root handle 1
        echo "traffic control rules removed"
        exit 0
        ;;
    restart)
        $0 stop
        $0 start
        exit 0
        ;;
    show)
        echo;echo " ---- qdiscs details -----"
        $TC -d qdisc show dev $PUBLIC_IF
        echo;echo " ---- qdiscs statistics --"
        $TC -s qdisc show dev $PUBLIC_IF
        exit 0
        ;;
    *)
        echo;echo "usage:$0 {start|stop|restart|show}"
        echo "load or stop the Traffic Control rules on the network interface"
        echo;echo "julien vehent - 2011 - julien@linuxwall.info"
        ;;
esac

class BaseConfigs:
    config3750 = """
srr-queue bandwidth share 1 30 35 5
priority-queue out 
udld port aggressive
no snmp trap link-status
mls qos trust device cisco-phone
spanning-tree portfast
spanning-tree bpduguard enable
ip dhcp snooping limit rate 20
    """
    config3850 = """
trust device cisco-phone
udld port aggressive
no snmp trap link-status
spanning-tree portfast
spanning-tree bpduguard enable
ip dhcp snooping limit rate 20
    """
    config9300 = """
trust device cisco-phone
auto qos voip cisco-phone 
spanning-tree portfast
service-policy input AutoQos-4.0-CiscoPhone-Input-Policy
service-policy output AutoQos-4.0-Output-Policy
    """

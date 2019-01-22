class BaseTemplates:
    template3750 = """srr-queue bandwidth share 1 30 35 5
priority-queue out 
udld port aggressive
no snmp trap link-status
mls qos trust device cisco-phone
spanning-tree portfast
spanning-tree bpduguard enable
ip dhcp snooping limit rate 20
"""
    template3850 = """trust device cisco-phone
udld port aggressive
no snmp trap link-status
spanning-tree portfast
spanning-tree bpduguard enable
ip dhcp snooping limit rate 20
"""
    template9300 = """trust device cisco-phone
auto qos voip cisco-phone 
spanning-tree portfast
service-policy input AutoQos-4.0-CiscoPhone-Input-Policy
service-policy output AutoQos-4.0-Output-Policy
"""
    template3560 = """srr-queue bandwidth share 1 30 35 5
priority-queue out
mls qos trust device cisco-phone
mls qos trust cos
auto qos voip cisco-phone
"""
    template2960 = """switchport port-security violation  protect
switchport port-security aging time 1
switchport port-security aging type inactivity
ip arp inspection limit rate 40
udld port aggressive
no snmp trap link-status
spanning-tree portfast
spanning-tree bpduguard enable
ip verify source
ip dhcp snooping limit rate 20
"""

    @staticmethod
    def __empty3560(switchConfig):
        if "mls qos trust" not in switchConfig:
            return True
        if "auto qos voip" not in switchConfig:
            return True
        if "bandwidth share" not in switchConfig:
            return True
        return False

    @staticmethod
    def __empty9300(switchConfig):
        if "trust device" not in switchConfig:
            return True
        if "spanning-tree" not in switchConfig:
            return True
        if "service-policy" not in switchConfig:
            return True
        if "auto qos voip" not in switchConfig:
            return True
        return False

    @staticmethod
    def __emptyBase(switchConfig):
        if "udld port aggressive" not in switchConfig:
            return True
        if "spanning-tree" not in switchConfig:
            return True
        if "ip dhcp snooping" not in switchConfig:
            return True
        if "no snmp trap" not in switchConfig:
            return True
        return False

    @staticmethod
    def isInterfaceEmpty(switchConfig, switchType):
        if switchType == "3560":
            return BaseTemplates.__empty3560(switchConfig)
        elif switchType == "9300":
            return BaseTemplates.__empty9300(switchConfig)
        else:
            return BaseTemplates.__emptyBase(switchConfig)

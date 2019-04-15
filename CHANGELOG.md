# Changelog

An incomplete log of larry growing up.

# 0.50 [[Beta 2 Release](https://github.com/Changer098/larry/releases/tag/0.50)]
- Added support for activating UPSs and APs
- Added support for the Ssh client not having to request '--MORE--' every time
- Should fix issues retrieving global voice vlan

# 0.49.1
- Fix IOS so that an addVlan can take a string object or a vlan object
- Investigating issue where risque doesn't return any voip info even though voip data exists

# 0.49
- Fix issues with VoIP and not matching up with risque

# 0.48.1 and 0.48.2 (Bug Fix release)
- Log when VoIP info can't be verified/configured

# 0.48
- Added Before/After Logging (logs the configuration before any changes are applied and after changes are applied)
- Moved logs folder and the persistence file from ```larry/``` to ```larry-data/```
- Modifies will now check if the port is shutdown and enable the port if it is.
- Barnacle bopping

# 0.47
- Implemented Verifying Repairs
- Fixed help formatting
- Allowed the ability to disable the vrf workaround
- Allowed the ability to disable color output

# 0.46
- Implemented Persistence; login once, securely saves credentials
- Included initial fixes for socket timeouts caused by long responses and adjusting for VRF
- Reduced number of VRF affected checks when running
- Bug wrangling

# 0.45

- Implemented VRF Workaround ([List of affected devices](https://1drv.ms/x/s!Am7FgEBKIICGia17HGoi-OeXzGaIHw))
- Started work on session storage, Disabled in release

# 0.40 [[Beta Release](https://github.com/Changer098/larry/releases/tag/0.40)]

- Implemented logging
- UI/bug fixes

# 0.36 [[Features Release](https://github.com/Changer098/larry/releases/tag/0.36)]

- Activate/Modify/Deactivate working on normal access ports, FEX ports, and trunk ports
- Verification works for each as well
- Configuration/Verification with Base Templates is implemented as well
- Updated executable to fix argument passing

# 0.35

- Added support for trunk ports (semi-tested) and FEX ports (needs more testing)
- Added support for Template Based configuration, determining whether a port is empty is still wonky

# 0.1.2 [[Initial Release](https://github.com/Changer098/larry/releases/tag/0.1.2)]

- Basic Verification working
- Basic Activation/Deactivation/Modify working

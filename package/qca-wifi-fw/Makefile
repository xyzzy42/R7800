include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=qca-wifi-fw
PKG_BRANCH:=master
PKG_VERSION:=QCA9984_hw_1-CNSS.BL.3.0.2-00068-S-1.59256.1
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=none-$(PKG_SOURCE)
PKG_BUILD_DIR:=$(BUILD_DIR)/QCA9984

-include $(INCLUDE_DIR)/package-version-override.mk
include $(INCLUDE_DIR)/package.mk

# Maybe there are other versions besides asic?

define Package/qca-wifi-fw-asic
  SECTION:=kernel
  CATEGORY:=Kernel modules
  SUBMENU:=Network Devices
  DEPENDS:=@TARGET_ipq806x
  TITLE:=Atheros Wifi firmware binaries
  PROVIDES:=qca-wifi-fw-hw1-10-4-asic
  MENU:=1
endef

define Package/qca-wifi-fw-asic/description
This package contains the Wifi firmware for QCA9984 chipset
endef

define Package/qca-wifi-fw-asic/config
	$(call Package/qca-wifi-fw-asic/override_source_path,qca-wifi-fw-asic)
endef

define Build/Configure
endef

define Build/Compile
endef

define Package/qca-wifi-fw-asic/install
	$(INSTALL_DIR) $(1)/lib/firmware/QCA9984
	$(CP) -r $(PKG_BUILD_DIR)/hw.1 $(1)/lib/firmware/QCA9984
endef

$(eval $(call BuildPackage,qca-wifi-fw-asic))

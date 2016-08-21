# -*- coding: utf-8 -*-
from app import Plugin
from app import kernel

@kernel.container.register('proxy_manager', ['@config.proxy', '@pgoapi', '@event_manager', '@logger'], tags=['plugin'])
class ProxyManager(Plugin):
    """
    # ----
    # Plugin: Proxy Manager
    # Desription: Handles proxy server related things.
    # ----
    """
    current_proxy = None
    proxy_blacklist = []

    def __init__(self, config_plugin, pgoapi, event_manager, logger):
        self.config_plugin = config_plugin
        self.pgoapi = pgoapi
        self.event_manager = event_manager
        self.logger = logger.getLogger('Proxy')

        # register events
        self.event_manager.add_listener('network_ipban', self.event_ipban, priority=0)

        # Config Deprecated?
        if self.config_plugin is None:
            self.error("Configuration Deprecated: Please see proxy.yml.example to add your proxy configuration!", "red")
        else:
            # switch proxy if proxy should always be used
            if self.config_plugin['proxy']['mode'] == "required":
                self.logger.info('Proxy Mode = Required!.')
                self.switch_proxyserver()

    def event_ipban(self, exit_bot=True, delay=10):
        # check for existing config / disabled
        if self.config_plugin is None or self.config_plugin['proxy']['enabled'] is False:
            return

        # notice
        self.logger.warning('Your IP address is most likely blocked or your proxy may is down.')

        # do not quit
        exit_bot = False

        # blacklist current proxy
        if self.current_proxy is not None:
            proxy_blacklist.append(self.current_proxy)

        # change proxy
        self.switch_proxyserver()
        self.logger.info('Waiting {} seconds before reconnecting ...'.format(delay))

        # wait
        time.sleep(delay)

    def switch_proxyserver(self):
        # check for existing config / disabled
        if self.config_plugin is None or self.config_plugin['proxy']['enabled'] is False:
            return

        proxy = self._find_proxy()
        if proxy is not None:
            self._set_proxy_server(proxy)
        else:
            self.logger.warning('No proxy servers remaining! Resetting the blacklist ...')
            self.proxy_blacklist = {}
            self.switch_proxyserver()

    def _find_proxy(self):
        for proxy_id in self.config_plugin['proxylist']:
            if proxy_id not in self.proxy_blacklist:
                proxy = self.config_plugin['proxylist'][proxy_id]

                # check if proxy is enabled
                if proxy['enabled'] is True:
                    return proxy

        return None

    def _set_proxy_server(self, proxy):
        proxies = None
        # the proxy types
        if proxy['type'] == "http" or proxy['type'] == "https":
            proxies = dict(
                http='{}'.format(proxy['address']),
                https='{}'.format(proxy['address'])
            )
        if proxy['type'] == "socks5":
            proxies = dict(
                http='{}://{}'.format(proxy['type'], proxy['address']),
                https='{}://{}'.format(proxy['type'], proxy['address'])
            )
        # set proxy
        self.pgoapi.set_proxy(proxies)
        self.logger.info('Changed to proxy server {} [{}].'.format(proxy['address'], proxy['type']))

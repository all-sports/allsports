import urllib,urllib2,re,cookielib,string,os,xbmc, xbmcgui, xbmcaddon, xbmcplugin, random
from t0mm0.common.net import Net as net

addon_id        = 'plugin.video.allsports'
selfAddon       = xbmcaddon.Addon(id=addon_id)
datapath        = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
cookie_file     = os.path.join(os.path.join(datapath,''), 'allsports.lwp')
user            = selfAddon.getSetting('hqusername')
passw           = selfAddon.getSetting('hqpassword')

if user == '' or passw == '':
    if os.path.exists(cookie_file):
        try: os.remove(cookie_file)
        except: pass
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Allsports', 'Please enter your Allsports account details','or register if you dont have an account','at www.streamingwizard.net','Cancel','Login')
    if ret == 1:
        keyb = xbmc.Keyboard('', 'Enter Username')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = keyb.getText()
            username=search
            keyb = xbmc.Keyboard('', 'Enter Password:')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = keyb.getText()
                password=search
                selfAddon.setSetting('hqusername',username)
                selfAddon.setSetting('hqpassword',password)
user = selfAddon.getSetting('hqusername')
passw = selfAddon.getSetting('hqpassword')

#############################################################################################################################

def setCookie(srDomain):
        html = net().http_GET(srDomain).content
        r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
        post_data = {}
        post_data['amember_login'] = user
        post_data['amember_pass'] = passw
        for name, value in r:
            post_data[name] = value
        net().http_GET('http://www.streamingwizard.net/amember/member')
        net().http_POST('http://www.streamingwizard.net/amember/member',post_data)
        net().save_cookies(cookie_file)
        net().set_cookies(cookie_file)

def MAINSA():
    setCookie('http://www.streamingwizard.net/amember/member')
    response = net().http_GET('http://www.streamingwizard.net/amember/member')
    if not 'Edit Profile' in response.content:
        dialog = xbmcgui.Dialog()
        dialog.ok('Allsports', 'Invalid login','Please check your Allsports account details in Add-on settings','')
        quit()
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    
    xbmc.sleep(1000)
   #free=re.compile('<li><a href="(.+?)">Sports Streams</a>').findall(link)[0]
    
    vip=re.compile('<li><a href="(.+?)">vip</a>').findall(link)
    if len(vip)>0:
        vip=vip[0]
        addDir('[COLOR lime]Subscription[/COLOR] Streams','http://www.streamingwizard.net/amember/vip/vip.php',2,icon,fanart)
    
    addLink('[COLOR yellow]How to Subscribe[/COLOR]','url',100,icon,fanart)
    addDir('Allsports Account Status','url',200,icon,fanart)
    addLink('Allsports Support','url',300,icon,fanart)

def getchannels(url):
    if 'vip' in url:baseurl = 'http://www.streamingwizard.net/amember/vip/'
    else:baseurl = 'http://www.streamingwizard.net/amember/vip/'
    setCookie('http://www.streamingwizard.net/amember/member')
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match=re.compile('<a href="(.+?)"></br><font color= "\#fff" size="\+1"><b>(.+?)</b>').findall(link)
    for url,channel in match:
        url = baseurl+url
        addLink(channel,url,3,icon,fanart)

def getstreams(url,name):
    setCookie('http://www.streamingwizard.net/amember/member')
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    swf='http://p.jwpcdn.com/6/11/jwplayer.flash.swf'
    strurl=re.compile("file: '(.+?)',").findall(link)[0]
    playable = strurl+' swfUrl='+swf+' pageUrl='+url+' live=true timeout=20 token=WY846p1E1g15W7s'
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    try:
        xbmc.Player ().play(playable, liz, False)
    except:
        pass
   
def account():
    setCookie('http://www.streamingwizard.net/amember/member')
    response = net().http_GET('http://www.streamingwizard.net/amember/member')
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    stat = ''
    user=re.compile('<div class="am-user-identity-block">(.+?)<').findall(link)[0]
    user = user+'\n'+' '
    accnt=re.compile('<li><strong>(.+?)</strong>(.+?)</li>').findall(link)
    for one,two in accnt:
        one = '[COLOR lime]'+one+'[/COLOR]'
        stat = stat+' '+one+' '+two+'\n'
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR yellow]Allsports Account Status[/COLOR]', '',stat,'')
    #quit()
  

def support():
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR blue]Allsports Account Support[/COLOR]', 'For account queries please contact us at:','info@allsportshub.net (via Email)')
    #quit()
       
def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
    
def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def notification(title, message, ms, nart):
    xbmc.executebuiltin("XBMC.notification(" + title + "," + message + "," + ms + "," + nart + ")")

def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def subscribe():
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR blue]To Subscribe[/COLOR]', 'To Subscribe visit:','streamingwizard.net/amember/signup',)
    
    

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
              
params=get_params(); url=None; name=None; mode=None; iconimage=None
try:url=urllib.unquote_plus(params["url"])
except:pass
try:name=urllib.unquote_plus(params["name"])
except:pass
try:mode=int(params["mode"])
except:pass
try:iconimage=urllib.unquote_plus(params["iconimage"])
except:pass

print "Mode: "+str(mode); print "Name: "+str(name); print "Thumb: "+str(iconimage)

if mode==None or url==None or len(url)<1:MAINSA()




elif mode==100:subscribe()
elif mode==200:account()
elif mode==300:support()



import urlparse,sys
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))


try:
    action = params['action']
except:
    action = None
try:
    name = params['name']
except:
    name = '0'
try:
    url = params['url']
except:
    url = '0'
try:
    playable = params['playable']
except:
    playable = '0'
try:
    content = params['content']
except:
    content = '0'
try:
    tvshow = params['tvshow']
except:
    tvshow = '0'
try:
    audio = params['audio']
except:
    audio = '0'
try:
    image = params['image']
except:
    image = '0'
try:
    fanart = params['fanart']
except:
    fanart = '0'




if action == None:
    from resources.lib.indexers import phstreams
    phstreams.getCategory()

elif action == 'dmode' or action == 'ndmode':
    from resources.lib.indexers import phstreams
    phstreams.getDirectory(name, url, audio, image, fanart, playable, content)

elif action == 'subDirectory':
    from resources.lib.indexers import phstreams
    phstreams.subDirectory(name, url, audio, image, fanart, playable, tvshow, content)

elif action == 'localDirectory':
    from resources.lib.indexers import phstreams
    phstreams.localDirectory()

elif action == 'search':
    from resources.lib.indexers import phstreams
    phstreams.getSearch()

elif action == 'searchDirectory':
    from resources.lib.indexers import phstreams
    phstreams.searchDirectory()

elif action == 'searchDirectory2':
    from resources.lib.indexers import phstreams
    phstreams.searchDirectory(url)

elif action == 'clearSearch':
    from resources.lib.indexers import phstreams
    phstreams.clearSearch()

elif action == 'resolveUrl':
    from resources.lib.indexers import phstreams
    phstreams.resolveUrl(name, url, audio, image, fanart, playable, content)

elif action == 'HuddleDirectory':
    from resources.lib.indexers import phhuddle
    phhuddle.HuddleDirectory()

elif action == 'Huddle_Main':
    from resources.lib.indexers import phhuddle
    phhuddle.Huddle_Main(url, image, fanart)

elif action == 'Archive_Main':
    from resources.lib.indexers import phhuddle
    phhuddle.Archive_Main(url, image, fanart)

elif action == 'Play_Main':
    from resources.lib.indexers import phhuddle
    phhuddle.Play_Main(url)

elif action == 'NBANFL_ARC':
    from resources.lib.indexers import phhuddle
    phhuddle.NBANFL_ARC(url, image, fanart)

elif action == 'NHL_ARC':
    from resources.lib.indexers import phhuddle
    phhuddle.NHL_ARC(url, image, fanart)

elif action == 'Huddle_Sites':
    from resources.lib.indexers import phhuddle
    phhuddle.Huddle_Sites(url, image, fanart)

elif action == 'NBANFL_Stream':
    from resources.lib.indexers import phhuddle
    phhuddle.NBANFL_Stream(url, image, fanart)

elif action == 'NHL_Stream':
    from resources.lib.indexers import phhuddle
    phhuddle.NHL_Stream(url)
    
elif action == 'nhlDirectory':
    from resources.lib.indexers import nhlcom
    nhlcom.nhlDirectory()
        
elif action == 'nhlScoreboard':
    from resources.lib.indexers import nhlcom
    nhlcom.nhlScoreboard()

elif action == 'nhlArchives':
    from resources.lib.indexers import nhlcom
    nhlcom.nhlArchives()

elif action == 'nhlStreams':
    from resources.lib.indexers import nhlcom
    nhlcom.nhlStreams(name,url)

elif action == 'nhlResolve':
    from resources.lib.indexers import nhlcom
    nhlcom.nhlResolve(url)







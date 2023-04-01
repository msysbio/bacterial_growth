import requests

def getFile(url):
    r = requests.get(url)
    print(r)
    open('/Users/julia/bacterialGrowth_thesis/files/poulate.yml', 'wb').write(r.content)
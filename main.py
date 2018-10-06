import threading
import os


class MonitoraArquivo(threading.Thread):
    def __init__(self, nome_do_arquivo):
        self.nome = nome_do_arquivo
        if os.path.exists(self.nome):
            self.last_modified = os.path.getmtime(self.nome)
        else:
            self.last_modified = None
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if os.path.exists(self.nome) and os.path.getmtime(self.nome) != self.last_modified:
                self.last_modified = os.path.getmtime(self.nome)
                print('%s modified' % self.nome)
                file = open(self.nome,"r")
                print file.read().splitlines()
                file.close()

thread1 = MonitoraArquivo("arquivo.txt")
thread1.start()
thread2 = MonitoraArquivo("file.txt")
thread2.start()

print('to saindo da main, eh nois')

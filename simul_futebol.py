import random, math, operator, numpy


def ler_jogos(arq_jogos):
    f = open(arq_jogos)
    jogos = []
    i = 0
    for cada_linha in f:
        registro = [int(k) for k in cada_linha.split('\t')]
        jogos.append(registro)
        i = i+1
    f.close()
    return (jogos)

def ler_times(arq_times):
    f = open(arq_times)
    times = []
    for cada_linha in f:
        times.append(cada_linha.split('\n')[0])
    f.close()
    return(times)

def gen_gols(alfa, beta):
    lamb = alfa/beta
    g = 0
    x = -math.log(1- random.uniform(0, 1))
    while( x < lamb):
      x = x -math.log(1 - random.uniform(0, 1))
      g = g+1
    return(g)
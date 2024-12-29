
def start_end (level):
    if level==1:
        start=(0,0)
        end=(8,9)
        rows=9
        cols=10
    if level==2:
        start=(0,0)
        end=(9,11)
        rows=10
        cols=12
    if level==3:
        start=(10,0)
        end=(1,15)
        rows=12
        cols=16
    if level==4:
        start=(1,2)
        end=(11,15)
        rows=12
        cols=16
    if level==5:
        start=(11,0)
        end=(3,15)
        rows=12
        cols=16
    return start,end,rows,cols
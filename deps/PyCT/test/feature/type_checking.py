def type_checking(x):
    # assert type(x) is int
    assert type(int(x)) is int
    assert type(5) is int
    # assert type(z:=(y:=x)) is int
    assert type(z:=(y:=int(x))) is int
    assert type(z:=(y:=5)) is int
    if x > 10:
        print('A')
    else:
        print('B')
    print('C') if z > 5 else print('D')

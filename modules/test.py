

def test_func(data_loader):

    print("This is a test func!")
    print("Options are: ")
    for key in data_loader.options:
        print('- ', key)
    

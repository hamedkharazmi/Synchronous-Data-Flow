import networkx as nx
import matplotlib.pyplot as plt

# Required variables
actors_processing_time=[]
topology_matrix=[]
marking_vector=[]
system_clocks=0
current_clock=0
latency=0
latency_temp=0
throughput=0
throughput_temp=0
num_of_out_tokens=0
num_of_in_tokens=0
num_of_initial_tokens=0
max_token=0
out_print=""
result=""

# Read information from the file
def read_file():
    global actors_processing_time, topology_matrix, marking_vector, system_clocks, max_token
    reading_file= open ("config.txt","rt")
    reading_file.readline()
    actors_processing_time=[int (x) for x in reading_file.readline().split(",")]
    # print(len(actors_processing_time))
    reading_file.readline()
    reading_file.readline()
    rows=int(reading_file.readline().split(":")[1])
    for i in range(rows):
        a=[]
        a=[int(x) for x in reading_file.readline().split(",")]
        # print(len(a))
        topology_matrix.append(a)
    # print(len(topology_matrix))
    reading_file.readline()
    reading_file.readline()
    marking_vector=[int(x) for x in reading_file.readline().split(",")]
    # print(len(marking_vector))
    reading_file.readline()
    reading_file.readline()
    system_clocks=int(reading_file.readline().split(":")[1])
    max_token=int(reading_file.readline().split(":")[1])

# process_time variable is the delay that every actor has
# input variable        is the number and rate the actor inputs
# output variable       is the number and rate the actor outputs
# InProcess variable    Indicates whether the actor is busy or not
# timer variable        Indicates at what stage of processing the actor is
class actor:
    def __init__(self, process_time, input_actor, output_actor):
        self.process_time=int(process_time)
        self.input=input_actor
        self.output=output_actor
        self.InProcess=False
        self.timer=0

# Can the actor fire or not
def fireing(thisActor):
    if len(thisActor.input)==0:
        if num_of_in_tokens<max_token:
            return True
        else:
            return False
    inp=len(thisActor.input)
    for x in thisActor.input:
        if marking_vector[x[0]]>=x[1]:
            inp-=1
    if inp==0:
        return True
    return False

# Computing latency and throughput
def latency_and_throughput(token_number, token_time):
    global latency, throughput_temp, throughput
    if token_number == latency_temp:
        latency = token_time - first_fire_inputNode
        throughput_temp=token_time
    elif token_number == latency_temp+1 :
        throughput = "1/"+str(token_time-throughput_temp)

# print
def print_log(actor_token_number ,status, token_time):
    global result
    if status == "activated":
        result= result + "time "+ str(token_time) + ": actor " + str(actor_token_number) + " " + status +"<br>"
        if actor_token_number ==0 :
            result= result + "time "+ str(token_time) + ": SRC " + status +"<br>"
        elif actor_token_number == len(actors_processing_time) -1:
            result= result + "time "+ str(token_time) + ": SNK " + status +"<br>"
    elif status == "fired":
        result= result + "time "+ str(token_time) + ": actor " + str(actor_token_number) + " " + status +"<br>"
        if actor_token_number ==0 :
            result= result + "time "+ str(token_time) + ": SRC " + status +"<br>"
        elif actor_token_number == len(actors_processing_time) -1:
            result= result + "time "+ str(token_time) + ": SNK " + status +"<br>"
    elif status == "exited":
        result= result + "time "+ str(token_time) + ": out token " + str(actor_token_number) + " " + status + " from SNK" +"<br>"

# MAIN
# Make a list of the actors
read_file()
actor_list=[]
for i in range(len(actors_processing_time)):
    input_temp=[]
    output_temp=[]
    for j in range(len(topology_matrix)):
        if topology_matrix[j][i]>0:
            output_temp.append([j,topology_matrix[j][i]])
        elif topology_matrix[j][i]<0:
            input_temp.append([j,-1*topology_matrix[j][i]])
    actor_list.append(actor(actors_processing_time[i], input_temp, output_temp))
for x in marking_vector:
    num_of_initial_tokens+=x
#The overall cycle of the system
while (num_of_out_tokens<=num_of_initial_tokens+max_token and current_clock <= system_clocks):
    for thisActor in actor_list:
        if thisActor.InProcess:
            thisActor.timer+=1
            if thisActor.timer==thisActor.process_time:
                for x in thisActor.output:
                    marking_vector[x[0]]+=x[1]
                thisActor.timer=0
                thisActor.InProcess=False
                print_log( actor_list.index(thisActor) , "fired" , current_clock )

        if fireing(thisActor)==True and thisActor.InProcess==False:
            if actor_list.index(thisActor)==0:
                num_of_in_tokens+=1
                if num_of_in_tokens==1:
                    all_toknes=0
                    temp_tokens=0
                    first_fire_inputNode = current_clock
                    inputNode_edges= [i[0] for i in thisActor.input]
                    for x in marking_vector:
                        all_toknes+=x
                    for i in inputNode_edges:
                        temp_tokens += marking_vector[i]
                    latency_temp= all_toknes-temp_tokens+num_of_out_tokens+1
                    # for x in marking_vector:
                    #     all_toknes+=x + 1
                    # for i in :
                    #     temp_tokens += marking_vector[i]
                    # latency_temp= all_toknes-temp_tokens+num_of_out_tokens+1
            print_log(actor_list.index(thisActor),"activated",current_clock)


            # without latancy for SRC
            if actors_processing_time[0]==0 and actor_list.index(thisActor)==0:
                print_log(actor_list.index(thisActor),"fired",current_clock)
                for i in range (max_token-1):
                    print_log(actor_list.index(thisActor),"activated",current_clock)
                    print_log(actor_list.index(thisActor),"fired",current_clock)
                    
                # for x in thisActor.output:
                #     marking_vector[x[0]] += x[1]*max_token
                # num_of_in_tokens += max_token-1
                # thisActor.InProcess=False

                for x in thisActor.output:
                    marking_vector[x[0]] += x[1]*max_token
                num_of_in_tokens += max_token-1
                thisActor.InProcess=False
            else:    
                for x in thisActor.input:
                    marking_vector[x[0]]-=x[1]
                thisActor.InProcess=True

            if len(thisActor.output)==0:
                num_of_out_tokens+=1
                latency_and_throughput(num_of_out_tokens, current_clock)
                print_log (num_of_out_tokens, "exited", current_clock)
                thisActor.InProcess=False
    current_clock+=1

if num_of_out_tokens==0:
    print("No output token!")
if (latency == 0):
    if latency_temp ==0:
        print("Time too low")
    else:
        print("Not enough time")
    print("Not enough time")
else:  
    print ("Latency:",latency)
    print("Throughput:" , throughput)

# save to file
output_buffer=""
output_buffer+="var chromosome = '"+result+"';\n"
writing_file=open("files/variable.txt" ,'w')
writing_file.write(output_buffer)
writing_file.close()  

# drawing graph
g = nx.Graph()
edges=[]
for i in range ( len(topology_matrix) ):
    for j in range ( len(actors_processing_time)):
        if topology_matrix[i][j] > 0:
            node1=j
        elif topology_matrix[i][j] <0 :
            node2=j
    g.add_edge(node1,node2)
# nx.draw(g, with_labels = True) 
options = {
    'node_color': 'Cyan',
    'node_size': 300,
    'arrowstyle': '-|>',
    'arrowsize': 20,
}
# pos = nx.spring_layout(g)
nx.draw_networkx(g, with_labels = True, **options)
# nx.draw_networkx_edges(g, pos, arrows=True)
# G = nx.DiGraph(directed=True)
plt.savefig("graph.png")

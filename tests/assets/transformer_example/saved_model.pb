��
��
D
AddV2
x"T
y"T
z"T"
Ttype:
2	��
^
AssignVariableOp
resource
value"dtype"
dtypetype"
validate_shapebool( �
~
BiasAdd

value"T	
bias"T
output"T" 
Ttype:
2	"-
data_formatstringNHWC:
NHWCNCHW
N
Cast	
x"SrcT	
y"DstT"
SrcTtype"
DstTtype"
Truncatebool( 
h
ConcatV2
values"T*N
axis"Tidx
output"T"
Nint(0"	
Ttype"
Tidxtype0:
2	
8
Const
output"dtype"
valuetensor"
dtypetype
R
Einsum
inputs"T*N
output"T"
equationstring"
Nint(0"	
Ttype
�
GatherV2
params"Tparams
indices"Tindices
axis"Taxis
output"Tparams"

batch_dimsint "
Tparamstype"
Tindicestype:
2	"
Taxistype:
2	
.
Identity

input"T
output"T"	
Ttype
q
MatMul
a"T
b"T
product"T"
transpose_abool( "
transpose_bbool( "
Ttype:

2	
�
Mean

input"T
reduction_indices"Tidx
output"T"
	keep_dimsbool( " 
Ttype:
2	"
Tidxtype0:
2	
�
MergeV2Checkpoints
checkpoint_prefixes
destination_prefix"
delete_old_dirsbool("
allow_missing_filesbool( �
?
Mul
x"T
y"T
z"T"
Ttype:
2	�

NoOp
M
Pack
values"T*N
output"T"
Nint(0"	
Ttype"
axisint 
C
Placeholder
output"dtype"
dtypetype"
shapeshape:
�
Prod

input"T
reduction_indices"Tidx
output"T"
	keep_dimsbool( " 
Ttype:
2	"
Tidxtype0:
2	
f
Range
start"Tidx
limit"Tidx
delta"Tidx
output"Tidx" 
Tidxtype0:
2
	
@
ReadVariableOp
resource
value"dtype"
dtypetype�
E
Relu
features"T
activations"T"
Ttype:
2	
[
Reshape
tensor"T
shape"Tshape
output"T"	
Ttype"
Tshapetype0:
2	
�
ResourceGather
resource
indices"Tindices
output"dtype"

batch_dimsint "
validate_indicesbool("
dtypetype"
Tindicestype:
2	�
o
	RestoreV2

prefix
tensor_names
shape_and_slices
tensors2dtypes"
dtypes
list(type)(0�
.
Rsqrt
x"T
y"T"
Ttype:

2
l
SaveV2

prefix
tensor_names
shape_and_slices
tensors2dtypes"
dtypes
list(type)(0�
?
Select
	condition

t"T
e"T
output"T"	
Ttype
P
Shape

input"T
output"out_type"	
Ttype"
out_typetype0:
2	
H
ShardedFilename
basename	
shard

num_shards
filename
9
Softmax
logits"T
softmax"T"
Ttype:
2
G
SquaredDifference
x"T
y"T
z"T"
Ttype:

2	�
�
StatefulPartitionedCall
args2Tin
output2Tout"
Tin
list(type)("
Tout
list(type)("	
ffunc"
configstring "
config_protostring "
executor_typestring ��
@
StaticRegexFullMatch	
input

output
"
patternstring
2
StopGradient

input"T
output"T"	
Ttype
�
StridedSlice

input"T
begin"Index
end"Index
strides"Index
output"T"	
Ttype"
Indextype:
2	"

begin_maskint "
end_maskint "
ellipsis_maskint "
new_axis_maskint "
shrink_axis_maskint 
N

StringJoin
inputs*N

output"
Nint(0"
	separatorstring 
<
Sub
x"T
y"T
z"T"
Ttype:
2	
P
	Transpose
x"T
perm"Tperm
y"T"	
Ttype"
Tpermtype0:
2	
�
VarHandleOp
resource"
	containerstring "
shared_namestring "
dtypetype"
shapeshape"#
allowed_deviceslist(string)
 �"serve*2.10.02v2.10.0-rc3-6-g359c3cdfc5f8ɗ
�
5Adam/transformer_block_2/layer_normalization_5/beta/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*F
shared_name75Adam/transformer_block_2/layer_normalization_5/beta/v
�
IAdam/transformer_block_2/layer_normalization_5/beta/v/Read/ReadVariableOpReadVariableOp5Adam/transformer_block_2/layer_normalization_5/beta/v*
_output_shapes
:*
dtype0
�
6Adam/transformer_block_2/layer_normalization_5/gamma/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*G
shared_name86Adam/transformer_block_2/layer_normalization_5/gamma/v
�
JAdam/transformer_block_2/layer_normalization_5/gamma/v/Read/ReadVariableOpReadVariableOp6Adam/transformer_block_2/layer_normalization_5/gamma/v*
_output_shapes
:*
dtype0
�
5Adam/transformer_block_2/layer_normalization_4/beta/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*F
shared_name75Adam/transformer_block_2/layer_normalization_4/beta/v
�
IAdam/transformer_block_2/layer_normalization_4/beta/v/Read/ReadVariableOpReadVariableOp5Adam/transformer_block_2/layer_normalization_4/beta/v*
_output_shapes
:*
dtype0
�
6Adam/transformer_block_2/layer_normalization_4/gamma/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*G
shared_name86Adam/transformer_block_2/layer_normalization_4/gamma/v
�
JAdam/transformer_block_2/layer_normalization_4/gamma/v/Read/ReadVariableOpReadVariableOp6Adam/transformer_block_2/layer_normalization_4/gamma/v*
_output_shapes
:*
dtype0
~
Adam/dense_9/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*$
shared_nameAdam/dense_9/bias/v
w
'Adam/dense_9/bias/v/Read/ReadVariableOpReadVariableOpAdam/dense_9/bias/v*
_output_shapes
:*
dtype0
�
Adam/dense_9/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*&
shared_nameAdam/dense_9/kernel/v

)Adam/dense_9/kernel/v/Read/ReadVariableOpReadVariableOpAdam/dense_9/kernel/v*
_output_shapes

:*
dtype0
~
Adam/dense_8/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*$
shared_nameAdam/dense_8/bias/v
w
'Adam/dense_8/bias/v/Read/ReadVariableOpReadVariableOpAdam/dense_8/bias/v*
_output_shapes
:*
dtype0
�
Adam/dense_8/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*&
shared_nameAdam/dense_8/kernel/v

)Adam/dense_8/kernel/v/Read/ReadVariableOpReadVariableOpAdam/dense_8/kernel/v*
_output_shapes

:*
dtype0
�
GAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*X
shared_nameIGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/v
�
[Adam/transformer_block_2/multi_head_attention_2/attention_output/bias/v/Read/ReadVariableOpReadVariableOpGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/v*
_output_shapes
:*
dtype0
�
IAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*Z
shared_nameKIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/v
�
]Adam/transformer_block_2/multi_head_attention_2/attention_output/kernel/v/Read/ReadVariableOpReadVariableOpIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/v*"
_output_shapes
:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/value/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/value/bias/v
�
PAdam/transformer_block_2/multi_head_attention_2/value/bias/v/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/value/bias/v*
_output_shapes

:*
dtype0
�
>Adam/transformer_block_2/multi_head_attention_2/value/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*O
shared_name@>Adam/transformer_block_2/multi_head_attention_2/value/kernel/v
�
RAdam/transformer_block_2/multi_head_attention_2/value/kernel/v/Read/ReadVariableOpReadVariableOp>Adam/transformer_block_2/multi_head_attention_2/value/kernel/v*"
_output_shapes
:*
dtype0
�
:Adam/transformer_block_2/multi_head_attention_2/key/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*K
shared_name<:Adam/transformer_block_2/multi_head_attention_2/key/bias/v
�
NAdam/transformer_block_2/multi_head_attention_2/key/bias/v/Read/ReadVariableOpReadVariableOp:Adam/transformer_block_2/multi_head_attention_2/key/bias/v*
_output_shapes

:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/key/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/key/kernel/v
�
PAdam/transformer_block_2/multi_head_attention_2/key/kernel/v/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/key/kernel/v*"
_output_shapes
:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/query/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/query/bias/v
�
PAdam/transformer_block_2/multi_head_attention_2/query/bias/v/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/query/bias/v*
_output_shapes

:*
dtype0
�
>Adam/transformer_block_2/multi_head_attention_2/query/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*O
shared_name@>Adam/transformer_block_2/multi_head_attention_2/query/kernel/v
�
RAdam/transformer_block_2/multi_head_attention_2/query/kernel/v/Read/ReadVariableOpReadVariableOp>Adam/transformer_block_2/multi_head_attention_2/query/kernel/v*"
_output_shapes
:*
dtype0
�
<Adam/token_and_position_embedding_2/embedding_5/embeddings/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:d*M
shared_name><Adam/token_and_position_embedding_2/embedding_5/embeddings/v
�
PAdam/token_and_position_embedding_2/embedding_5/embeddings/v/Read/ReadVariableOpReadVariableOp<Adam/token_and_position_embedding_2/embedding_5/embeddings/v*
_output_shapes

:d*
dtype0
�
<Adam/token_and_position_embedding_2/embedding_4/embeddings/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:	�*M
shared_name><Adam/token_and_position_embedding_2/embedding_4/embeddings/v
�
PAdam/token_and_position_embedding_2/embedding_4/embeddings/v/Read/ReadVariableOpReadVariableOp<Adam/token_and_position_embedding_2/embedding_4/embeddings/v*
_output_shapes
:	�*
dtype0
�
Adam/dense_11/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*%
shared_nameAdam/dense_11/bias/v
y
(Adam/dense_11/bias/v/Read/ReadVariableOpReadVariableOpAdam/dense_11/bias/v*
_output_shapes
:*
dtype0
�
Adam/dense_11/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*'
shared_nameAdam/dense_11/kernel/v
�
*Adam/dense_11/kernel/v/Read/ReadVariableOpReadVariableOpAdam/dense_11/kernel/v*
_output_shapes

:*
dtype0
�
Adam/dense_10/bias/vVarHandleOp*
_output_shapes
: *
dtype0*
shape:*%
shared_nameAdam/dense_10/bias/v
y
(Adam/dense_10/bias/v/Read/ReadVariableOpReadVariableOpAdam/dense_10/bias/v*
_output_shapes
:*
dtype0
�
Adam/dense_10/kernel/vVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*'
shared_nameAdam/dense_10/kernel/v
�
*Adam/dense_10/kernel/v/Read/ReadVariableOpReadVariableOpAdam/dense_10/kernel/v*
_output_shapes

:*
dtype0
�
5Adam/transformer_block_2/layer_normalization_5/beta/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*F
shared_name75Adam/transformer_block_2/layer_normalization_5/beta/m
�
IAdam/transformer_block_2/layer_normalization_5/beta/m/Read/ReadVariableOpReadVariableOp5Adam/transformer_block_2/layer_normalization_5/beta/m*
_output_shapes
:*
dtype0
�
6Adam/transformer_block_2/layer_normalization_5/gamma/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*G
shared_name86Adam/transformer_block_2/layer_normalization_5/gamma/m
�
JAdam/transformer_block_2/layer_normalization_5/gamma/m/Read/ReadVariableOpReadVariableOp6Adam/transformer_block_2/layer_normalization_5/gamma/m*
_output_shapes
:*
dtype0
�
5Adam/transformer_block_2/layer_normalization_4/beta/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*F
shared_name75Adam/transformer_block_2/layer_normalization_4/beta/m
�
IAdam/transformer_block_2/layer_normalization_4/beta/m/Read/ReadVariableOpReadVariableOp5Adam/transformer_block_2/layer_normalization_4/beta/m*
_output_shapes
:*
dtype0
�
6Adam/transformer_block_2/layer_normalization_4/gamma/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*G
shared_name86Adam/transformer_block_2/layer_normalization_4/gamma/m
�
JAdam/transformer_block_2/layer_normalization_4/gamma/m/Read/ReadVariableOpReadVariableOp6Adam/transformer_block_2/layer_normalization_4/gamma/m*
_output_shapes
:*
dtype0
~
Adam/dense_9/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*$
shared_nameAdam/dense_9/bias/m
w
'Adam/dense_9/bias/m/Read/ReadVariableOpReadVariableOpAdam/dense_9/bias/m*
_output_shapes
:*
dtype0
�
Adam/dense_9/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*&
shared_nameAdam/dense_9/kernel/m

)Adam/dense_9/kernel/m/Read/ReadVariableOpReadVariableOpAdam/dense_9/kernel/m*
_output_shapes

:*
dtype0
~
Adam/dense_8/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*$
shared_nameAdam/dense_8/bias/m
w
'Adam/dense_8/bias/m/Read/ReadVariableOpReadVariableOpAdam/dense_8/bias/m*
_output_shapes
:*
dtype0
�
Adam/dense_8/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*&
shared_nameAdam/dense_8/kernel/m

)Adam/dense_8/kernel/m/Read/ReadVariableOpReadVariableOpAdam/dense_8/kernel/m*
_output_shapes

:*
dtype0
�
GAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*X
shared_nameIGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/m
�
[Adam/transformer_block_2/multi_head_attention_2/attention_output/bias/m/Read/ReadVariableOpReadVariableOpGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/m*
_output_shapes
:*
dtype0
�
IAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*Z
shared_nameKIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/m
�
]Adam/transformer_block_2/multi_head_attention_2/attention_output/kernel/m/Read/ReadVariableOpReadVariableOpIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/m*"
_output_shapes
:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/value/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/value/bias/m
�
PAdam/transformer_block_2/multi_head_attention_2/value/bias/m/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/value/bias/m*
_output_shapes

:*
dtype0
�
>Adam/transformer_block_2/multi_head_attention_2/value/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*O
shared_name@>Adam/transformer_block_2/multi_head_attention_2/value/kernel/m
�
RAdam/transformer_block_2/multi_head_attention_2/value/kernel/m/Read/ReadVariableOpReadVariableOp>Adam/transformer_block_2/multi_head_attention_2/value/kernel/m*"
_output_shapes
:*
dtype0
�
:Adam/transformer_block_2/multi_head_attention_2/key/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*K
shared_name<:Adam/transformer_block_2/multi_head_attention_2/key/bias/m
�
NAdam/transformer_block_2/multi_head_attention_2/key/bias/m/Read/ReadVariableOpReadVariableOp:Adam/transformer_block_2/multi_head_attention_2/key/bias/m*
_output_shapes

:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/key/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/key/kernel/m
�
PAdam/transformer_block_2/multi_head_attention_2/key/kernel/m/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/key/kernel/m*"
_output_shapes
:*
dtype0
�
<Adam/transformer_block_2/multi_head_attention_2/query/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*M
shared_name><Adam/transformer_block_2/multi_head_attention_2/query/bias/m
�
PAdam/transformer_block_2/multi_head_attention_2/query/bias/m/Read/ReadVariableOpReadVariableOp<Adam/transformer_block_2/multi_head_attention_2/query/bias/m*
_output_shapes

:*
dtype0
�
>Adam/transformer_block_2/multi_head_attention_2/query/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*O
shared_name@>Adam/transformer_block_2/multi_head_attention_2/query/kernel/m
�
RAdam/transformer_block_2/multi_head_attention_2/query/kernel/m/Read/ReadVariableOpReadVariableOp>Adam/transformer_block_2/multi_head_attention_2/query/kernel/m*"
_output_shapes
:*
dtype0
�
<Adam/token_and_position_embedding_2/embedding_5/embeddings/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:d*M
shared_name><Adam/token_and_position_embedding_2/embedding_5/embeddings/m
�
PAdam/token_and_position_embedding_2/embedding_5/embeddings/m/Read/ReadVariableOpReadVariableOp<Adam/token_and_position_embedding_2/embedding_5/embeddings/m*
_output_shapes

:d*
dtype0
�
<Adam/token_and_position_embedding_2/embedding_4/embeddings/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:	�*M
shared_name><Adam/token_and_position_embedding_2/embedding_4/embeddings/m
�
PAdam/token_and_position_embedding_2/embedding_4/embeddings/m/Read/ReadVariableOpReadVariableOp<Adam/token_and_position_embedding_2/embedding_4/embeddings/m*
_output_shapes
:	�*
dtype0
�
Adam/dense_11/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*%
shared_nameAdam/dense_11/bias/m
y
(Adam/dense_11/bias/m/Read/ReadVariableOpReadVariableOpAdam/dense_11/bias/m*
_output_shapes
:*
dtype0
�
Adam/dense_11/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*'
shared_nameAdam/dense_11/kernel/m
�
*Adam/dense_11/kernel/m/Read/ReadVariableOpReadVariableOpAdam/dense_11/kernel/m*
_output_shapes

:*
dtype0
�
Adam/dense_10/bias/mVarHandleOp*
_output_shapes
: *
dtype0*
shape:*%
shared_nameAdam/dense_10/bias/m
y
(Adam/dense_10/bias/m/Read/ReadVariableOpReadVariableOpAdam/dense_10/bias/m*
_output_shapes
:*
dtype0
�
Adam/dense_10/kernel/mVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*'
shared_nameAdam/dense_10/kernel/m
�
*Adam/dense_10/kernel/m/Read/ReadVariableOpReadVariableOpAdam/dense_10/kernel/m*
_output_shapes

:*
dtype0
^
countVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_namecount
W
count/Read/ReadVariableOpReadVariableOpcount*
_output_shapes
: *
dtype0
^
totalVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nametotal
W
total/Read/ReadVariableOpReadVariableOptotal*
_output_shapes
: *
dtype0
b
count_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name	count_1
[
count_1/Read/ReadVariableOpReadVariableOpcount_1*
_output_shapes
: *
dtype0
b
total_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name	total_1
[
total_1/Read/ReadVariableOpReadVariableOptotal_1*
_output_shapes
: *
dtype0
x
Adam/learning_rateVarHandleOp*
_output_shapes
: *
dtype0*
shape: *#
shared_nameAdam/learning_rate
q
&Adam/learning_rate/Read/ReadVariableOpReadVariableOpAdam/learning_rate*
_output_shapes
: *
dtype0
h

Adam/decayVarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_name
Adam/decay
a
Adam/decay/Read/ReadVariableOpReadVariableOp
Adam/decay*
_output_shapes
: *
dtype0
j
Adam/beta_2VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nameAdam/beta_2
c
Adam/beta_2/Read/ReadVariableOpReadVariableOpAdam/beta_2*
_output_shapes
: *
dtype0
j
Adam/beta_1VarHandleOp*
_output_shapes
: *
dtype0*
shape: *
shared_nameAdam/beta_1
c
Adam/beta_1/Read/ReadVariableOpReadVariableOpAdam/beta_1*
_output_shapes
: *
dtype0
f
	Adam/iterVarHandleOp*
_output_shapes
: *
dtype0	*
shape: *
shared_name	Adam/iter
_
Adam/iter/Read/ReadVariableOpReadVariableOp	Adam/iter*
_output_shapes
: *
dtype0	
�
.transformer_block_2/layer_normalization_5/betaVarHandleOp*
_output_shapes
: *
dtype0*
shape:*?
shared_name0.transformer_block_2/layer_normalization_5/beta
�
Btransformer_block_2/layer_normalization_5/beta/Read/ReadVariableOpReadVariableOp.transformer_block_2/layer_normalization_5/beta*
_output_shapes
:*
dtype0
�
/transformer_block_2/layer_normalization_5/gammaVarHandleOp*
_output_shapes
: *
dtype0*
shape:*@
shared_name1/transformer_block_2/layer_normalization_5/gamma
�
Ctransformer_block_2/layer_normalization_5/gamma/Read/ReadVariableOpReadVariableOp/transformer_block_2/layer_normalization_5/gamma*
_output_shapes
:*
dtype0
�
.transformer_block_2/layer_normalization_4/betaVarHandleOp*
_output_shapes
: *
dtype0*
shape:*?
shared_name0.transformer_block_2/layer_normalization_4/beta
�
Btransformer_block_2/layer_normalization_4/beta/Read/ReadVariableOpReadVariableOp.transformer_block_2/layer_normalization_4/beta*
_output_shapes
:*
dtype0
�
/transformer_block_2/layer_normalization_4/gammaVarHandleOp*
_output_shapes
: *
dtype0*
shape:*@
shared_name1/transformer_block_2/layer_normalization_4/gamma
�
Ctransformer_block_2/layer_normalization_4/gamma/Read/ReadVariableOpReadVariableOp/transformer_block_2/layer_normalization_4/gamma*
_output_shapes
:*
dtype0
p
dense_9/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:*
shared_namedense_9/bias
i
 dense_9/bias/Read/ReadVariableOpReadVariableOpdense_9/bias*
_output_shapes
:*
dtype0
x
dense_9/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*
shared_namedense_9/kernel
q
"dense_9/kernel/Read/ReadVariableOpReadVariableOpdense_9/kernel*
_output_shapes

:*
dtype0
p
dense_8/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:*
shared_namedense_8/bias
i
 dense_8/bias/Read/ReadVariableOpReadVariableOpdense_8/bias*
_output_shapes
:*
dtype0
x
dense_8/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*
shared_namedense_8/kernel
q
"dense_8/kernel/Read/ReadVariableOpReadVariableOpdense_8/kernel*
_output_shapes

:*
dtype0
�
@transformer_block_2/multi_head_attention_2/attention_output/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:*Q
shared_nameB@transformer_block_2/multi_head_attention_2/attention_output/bias
�
Ttransformer_block_2/multi_head_attention_2/attention_output/bias/Read/ReadVariableOpReadVariableOp@transformer_block_2/multi_head_attention_2/attention_output/bias*
_output_shapes
:*
dtype0
�
Btransformer_block_2/multi_head_attention_2/attention_output/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape:*S
shared_nameDBtransformer_block_2/multi_head_attention_2/attention_output/kernel
�
Vtransformer_block_2/multi_head_attention_2/attention_output/kernel/Read/ReadVariableOpReadVariableOpBtransformer_block_2/multi_head_attention_2/attention_output/kernel*"
_output_shapes
:*
dtype0
�
5transformer_block_2/multi_head_attention_2/value/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*F
shared_name75transformer_block_2/multi_head_attention_2/value/bias
�
Itransformer_block_2/multi_head_attention_2/value/bias/Read/ReadVariableOpReadVariableOp5transformer_block_2/multi_head_attention_2/value/bias*
_output_shapes

:*
dtype0
�
7transformer_block_2/multi_head_attention_2/value/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape:*H
shared_name97transformer_block_2/multi_head_attention_2/value/kernel
�
Ktransformer_block_2/multi_head_attention_2/value/kernel/Read/ReadVariableOpReadVariableOp7transformer_block_2/multi_head_attention_2/value/kernel*"
_output_shapes
:*
dtype0
�
3transformer_block_2/multi_head_attention_2/key/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*D
shared_name53transformer_block_2/multi_head_attention_2/key/bias
�
Gtransformer_block_2/multi_head_attention_2/key/bias/Read/ReadVariableOpReadVariableOp3transformer_block_2/multi_head_attention_2/key/bias*
_output_shapes

:*
dtype0
�
5transformer_block_2/multi_head_attention_2/key/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape:*F
shared_name75transformer_block_2/multi_head_attention_2/key/kernel
�
Itransformer_block_2/multi_head_attention_2/key/kernel/Read/ReadVariableOpReadVariableOp5transformer_block_2/multi_head_attention_2/key/kernel*"
_output_shapes
:*
dtype0
�
5transformer_block_2/multi_head_attention_2/query/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape
:*F
shared_name75transformer_block_2/multi_head_attention_2/query/bias
�
Itransformer_block_2/multi_head_attention_2/query/bias/Read/ReadVariableOpReadVariableOp5transformer_block_2/multi_head_attention_2/query/bias*
_output_shapes

:*
dtype0
�
7transformer_block_2/multi_head_attention_2/query/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape:*H
shared_name97transformer_block_2/multi_head_attention_2/query/kernel
�
Ktransformer_block_2/multi_head_attention_2/query/kernel/Read/ReadVariableOpReadVariableOp7transformer_block_2/multi_head_attention_2/query/kernel*"
_output_shapes
:*
dtype0
�
5token_and_position_embedding_2/embedding_5/embeddingsVarHandleOp*
_output_shapes
: *
dtype0*
shape
:d*F
shared_name75token_and_position_embedding_2/embedding_5/embeddings
�
Itoken_and_position_embedding_2/embedding_5/embeddings/Read/ReadVariableOpReadVariableOp5token_and_position_embedding_2/embedding_5/embeddings*
_output_shapes

:d*
dtype0
�
5token_and_position_embedding_2/embedding_4/embeddingsVarHandleOp*
_output_shapes
: *
dtype0*
shape:	�*F
shared_name75token_and_position_embedding_2/embedding_4/embeddings
�
Itoken_and_position_embedding_2/embedding_4/embeddings/Read/ReadVariableOpReadVariableOp5token_and_position_embedding_2/embedding_4/embeddings*
_output_shapes
:	�*
dtype0
r
dense_11/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:*
shared_namedense_11/bias
k
!dense_11/bias/Read/ReadVariableOpReadVariableOpdense_11/bias*
_output_shapes
:*
dtype0
z
dense_11/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:* 
shared_namedense_11/kernel
s
#dense_11/kernel/Read/ReadVariableOpReadVariableOpdense_11/kernel*
_output_shapes

:*
dtype0
r
dense_10/biasVarHandleOp*
_output_shapes
: *
dtype0*
shape:*
shared_namedense_10/bias
k
!dense_10/bias/Read/ReadVariableOpReadVariableOpdense_10/bias*
_output_shapes
:*
dtype0
z
dense_10/kernelVarHandleOp*
_output_shapes
: *
dtype0*
shape
:* 
shared_namedense_10/kernel
s
#dense_10/kernel/Read/ReadVariableOpReadVariableOpdense_10/kernel*
_output_shapes

:*
dtype0
z
serving_default_input_3Placeholder*'
_output_shapes
:���������d*
dtype0*
shape:���������d
�	
StatefulPartitionedCallStatefulPartitionedCallserving_default_input_35token_and_position_embedding_2/embedding_5/embeddings5token_and_position_embedding_2/embedding_4/embeddings7transformer_block_2/multi_head_attention_2/query/kernel5transformer_block_2/multi_head_attention_2/query/bias5transformer_block_2/multi_head_attention_2/key/kernel3transformer_block_2/multi_head_attention_2/key/bias7transformer_block_2/multi_head_attention_2/value/kernel5transformer_block_2/multi_head_attention_2/value/biasBtransformer_block_2/multi_head_attention_2/attention_output/kernel@transformer_block_2/multi_head_attention_2/attention_output/bias/transformer_block_2/layer_normalization_4/gamma.transformer_block_2/layer_normalization_4/betadense_8/kerneldense_8/biasdense_9/kerneldense_9/bias/transformer_block_2/layer_normalization_5/gamma.transformer_block_2/layer_normalization_5/betadense_10/kerneldense_10/biasdense_11/kerneldense_11/bias*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *,
f'R%
#__inference_signature_wrapper_53639

NoOpNoOp
��
ConstConst"/device:CPU:0*
_output_shapes
: *
dtype0*��
value��B�� B��
�
layer-0
layer_with_weights-0
layer-1
layer_with_weights-1
layer-2
layer-3
layer-4
layer_with_weights-2
layer-5
layer-6
layer_with_weights-3
layer-7
		variables

trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
_default_save_signature
	optimizer

signatures*
* 
�
	variables
trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
	token_emb
pos_emb*
�
	variables
trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
 att
!ffn
"
layernorm1
#
layernorm2
$dropout1
%dropout2*
�
&	variables
'trainable_variables
(regularization_losses
)	keras_api
*__call__
*+&call_and_return_all_conditional_losses* 
�
,	variables
-trainable_variables
.regularization_losses
/	keras_api
0__call__
*1&call_and_return_all_conditional_losses
2_random_generator* 
�
3	variables
4trainable_variables
5regularization_losses
6	keras_api
7__call__
*8&call_and_return_all_conditional_losses

9kernel
:bias*
�
;	variables
<trainable_variables
=regularization_losses
>	keras_api
?__call__
*@&call_and_return_all_conditional_losses
A_random_generator* 
�
B	variables
Ctrainable_variables
Dregularization_losses
E	keras_api
F__call__
*G&call_and_return_all_conditional_losses

Hkernel
Ibias*
�
J0
K1
L2
M3
N4
O5
P6
Q7
R8
S9
T10
U11
V12
W13
X14
Y15
Z16
[17
918
:19
H20
I21*
�
J0
K1
L2
M3
N4
O5
P6
Q7
R8
S9
T10
U11
V12
W13
X14
Y15
Z16
[17
918
:19
H20
I21*
* 
�
\non_trainable_variables

]layers
^metrics
_layer_regularization_losses
`layer_metrics
		variables

trainable_variables
regularization_losses
__call__
_default_save_signature
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses*
6
atrace_0
btrace_1
ctrace_2
dtrace_3* 
6
etrace_0
ftrace_1
gtrace_2
htrace_3* 
* 
�
iiter

jbeta_1

kbeta_2
	ldecay
mlearning_rate9m�:m�Hm�Im�Jm�Km�Lm�Mm�Nm�Om�Pm�Qm�Rm�Sm�Tm�Um�Vm�Wm�Xm�Ym�Zm�[m�9v�:v�Hv�Iv�Jv�Kv�Lv�Mv�Nv�Ov�Pv�Qv�Rv�Sv�Tv�Uv�Vv�Wv�Xv�Yv�Zv�[v�*

nserving_default* 

J0
K1*

J0
K1*
* 
�
onon_trainable_variables

players
qmetrics
rlayer_regularization_losses
slayer_metrics
	variables
trainable_variables
regularization_losses
__call__
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses*

ttrace_0* 

utrace_0* 
�
v	variables
wtrainable_variables
xregularization_losses
y	keras_api
z__call__
*{&call_and_return_all_conditional_losses
J
embeddings*
�
|	variables
}trainable_variables
~regularization_losses
	keras_api
�__call__
+�&call_and_return_all_conditional_losses
K
embeddings*
z
L0
M1
N2
O3
P4
Q5
R6
S7
T8
U9
V10
W11
X12
Y13
Z14
[15*
z
L0
M1
N2
O3
P4
Q5
R6
S7
T8
U9
V10
W11
X12
Y13
Z14
[15*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
	variables
trainable_variables
regularization_losses
__call__
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses*

�trace_0
�trace_1* 

�trace_0
�trace_1* 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_query_dense
�
_key_dense
�_value_dense
�_softmax
�_dropout_layer
�_output_dense*
�
�layer_with_weights-0
�layer-0
�layer_with_weights-1
�layer-1
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
	�axis
	Xgamma
Ybeta*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
	�axis
	Zgamma
[beta*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator* 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
&	variables
'trainable_variables
(regularization_losses
*__call__
*+&call_and_return_all_conditional_losses
&+"call_and_return_conditional_losses* 

�trace_0* 

�trace_0* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
,	variables
-trainable_variables
.regularization_losses
0__call__
*1&call_and_return_all_conditional_losses
&1"call_and_return_conditional_losses* 

�trace_0
�trace_1* 

�trace_0
�trace_1* 
* 

90
:1*

90
:1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
3	variables
4trainable_variables
5regularization_losses
7__call__
*8&call_and_return_all_conditional_losses
&8"call_and_return_conditional_losses*

�trace_0* 

�trace_0* 
_Y
VARIABLE_VALUEdense_10/kernel6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUE*
[U
VARIABLE_VALUEdense_10/bias4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUE*
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
;	variables
<trainable_variables
=regularization_losses
?__call__
*@&call_and_return_all_conditional_losses
&@"call_and_return_conditional_losses* 

�trace_0
�trace_1* 

�trace_0
�trace_1* 
* 

H0
I1*

H0
I1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
B	variables
Ctrainable_variables
Dregularization_losses
F__call__
*G&call_and_return_all_conditional_losses
&G"call_and_return_conditional_losses*

�trace_0* 

�trace_0* 
_Y
VARIABLE_VALUEdense_11/kernel6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUE*
[U
VARIABLE_VALUEdense_11/bias4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUE*
uo
VARIABLE_VALUE5token_and_position_embedding_2/embedding_4/embeddings&variables/0/.ATTRIBUTES/VARIABLE_VALUE*
uo
VARIABLE_VALUE5token_and_position_embedding_2/embedding_5/embeddings&variables/1/.ATTRIBUTES/VARIABLE_VALUE*
wq
VARIABLE_VALUE7transformer_block_2/multi_head_attention_2/query/kernel&variables/2/.ATTRIBUTES/VARIABLE_VALUE*
uo
VARIABLE_VALUE5transformer_block_2/multi_head_attention_2/query/bias&variables/3/.ATTRIBUTES/VARIABLE_VALUE*
uo
VARIABLE_VALUE5transformer_block_2/multi_head_attention_2/key/kernel&variables/4/.ATTRIBUTES/VARIABLE_VALUE*
sm
VARIABLE_VALUE3transformer_block_2/multi_head_attention_2/key/bias&variables/5/.ATTRIBUTES/VARIABLE_VALUE*
wq
VARIABLE_VALUE7transformer_block_2/multi_head_attention_2/value/kernel&variables/6/.ATTRIBUTES/VARIABLE_VALUE*
uo
VARIABLE_VALUE5transformer_block_2/multi_head_attention_2/value/bias&variables/7/.ATTRIBUTES/VARIABLE_VALUE*
�|
VARIABLE_VALUEBtransformer_block_2/multi_head_attention_2/attention_output/kernel&variables/8/.ATTRIBUTES/VARIABLE_VALUE*
�z
VARIABLE_VALUE@transformer_block_2/multi_head_attention_2/attention_output/bias&variables/9/.ATTRIBUTES/VARIABLE_VALUE*
OI
VARIABLE_VALUEdense_8/kernel'variables/10/.ATTRIBUTES/VARIABLE_VALUE*
MG
VARIABLE_VALUEdense_8/bias'variables/11/.ATTRIBUTES/VARIABLE_VALUE*
OI
VARIABLE_VALUEdense_9/kernel'variables/12/.ATTRIBUTES/VARIABLE_VALUE*
MG
VARIABLE_VALUEdense_9/bias'variables/13/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUE/transformer_block_2/layer_normalization_4/gamma'variables/14/.ATTRIBUTES/VARIABLE_VALUE*
oi
VARIABLE_VALUE.transformer_block_2/layer_normalization_4/beta'variables/15/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUE/transformer_block_2/layer_normalization_5/gamma'variables/16/.ATTRIBUTES/VARIABLE_VALUE*
oi
VARIABLE_VALUE.transformer_block_2/layer_normalization_5/beta'variables/17/.ATTRIBUTES/VARIABLE_VALUE*
* 
<
0
1
2
3
4
5
6
7*

�0
�1*
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
LF
VARIABLE_VALUE	Adam/iter)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUE*
PJ
VARIABLE_VALUEAdam/beta_1+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUE*
PJ
VARIABLE_VALUEAdam/beta_2+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUE*
NH
VARIABLE_VALUE
Adam/decay*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUE*
^X
VARIABLE_VALUEAdam/learning_rate2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUE*
* 
* 

0
1*
* 
* 
* 
* 
* 

J0*

J0*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
v	variables
wtrainable_variables
xregularization_losses
z__call__
*{&call_and_return_all_conditional_losses
&{"call_and_return_conditional_losses*
* 
* 

K0*

K0*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
|	variables
}trainable_variables
~regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
.
 0
!1
"2
#3
$4
%5*
* 
* 
* 
* 
* 
* 
* 
<
L0
M1
N2
O3
P4
Q5
R6
S7*
<
L0
M1
N2
O3
P4
Q5
R6
S7*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Lkernel
Mbias*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Nkernel
Obias*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Pkernel
Qbias*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses* 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator* 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Rkernel
Sbias*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses

Tkernel
Ubias*
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses

Vkernel
Wbias*
 
T0
U1
V2
W3*
 
T0
U1
V2
W3*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
:
�trace_0
�trace_1
�trace_2
�trace_3* 
:
�trace_0
�trace_1
�trace_2
�trace_3* 

X0
Y1*

X0
Y1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 

Z0
[1*

Z0
[1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses* 
* 
* 
* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
<
�	variables
�	keras_api

�total

�count*
M
�	variables
�	keras_api

�total

�count
�
_fn_kwargs*
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
4
�0
�1
�2
�3
�4
�5*
* 
* 
* 

L0
M1*

L0
M1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
* 

N0
O1*

N0
O1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
* 

P0
Q1*

P0
Q1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses* 
* 
* 
* 
* 
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses* 
* 
* 
* 

R0
S1*

R0
S1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*
* 
* 
* 
* 

T0
U1*

T0
U1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*

�trace_0* 

�trace_0* 

V0
W1*

V0
W1*
* 
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses*

�trace_0* 

�trace_0* 
* 

�0
�1*
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 

�0
�1*

�	variables*
UO
VARIABLE_VALUEtotal_14keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUE*
UO
VARIABLE_VALUEcount_14keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUE*

�0
�1*

�	variables*
SM
VARIABLE_VALUEtotal4keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUE*
SM
VARIABLE_VALUEcount4keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUE*
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
* 
�|
VARIABLE_VALUEAdam/dense_10/kernel/mRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
~x
VARIABLE_VALUEAdam/dense_10/bias/mPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
�|
VARIABLE_VALUEAdam/dense_11/kernel/mRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
~x
VARIABLE_VALUEAdam/dense_11/bias/mPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/token_and_position_embedding_2/embedding_4/embeddings/mBvariables/0/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/token_and_position_embedding_2/embedding_5/embeddings/mBvariables/1/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE>Adam/transformer_block_2/multi_head_attention_2/query/kernel/mBvariables/2/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/query/bias/mBvariables/3/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/key/kernel/mBvariables/4/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE:Adam/transformer_block_2/multi_head_attention_2/key/bias/mBvariables/5/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE>Adam/transformer_block_2/multi_head_attention_2/value/kernel/mBvariables/6/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/value/bias/mBvariables/7/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUEIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/mBvariables/8/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUEGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/mBvariables/9/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
rl
VARIABLE_VALUEAdam/dense_8/kernel/mCvariables/10/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUEAdam/dense_8/bias/mCvariables/11/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
rl
VARIABLE_VALUEAdam/dense_9/kernel/mCvariables/12/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUEAdam/dense_9/bias/mCvariables/13/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE6Adam/transformer_block_2/layer_normalization_4/gamma/mCvariables/14/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE5Adam/transformer_block_2/layer_normalization_4/beta/mCvariables/15/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE6Adam/transformer_block_2/layer_normalization_5/gamma/mCvariables/16/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE5Adam/transformer_block_2/layer_normalization_5/beta/mCvariables/17/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUE*
�|
VARIABLE_VALUEAdam/dense_10/kernel/vRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
~x
VARIABLE_VALUEAdam/dense_10/bias/vPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
�|
VARIABLE_VALUEAdam/dense_11/kernel/vRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
~x
VARIABLE_VALUEAdam/dense_11/bias/vPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/token_and_position_embedding_2/embedding_4/embeddings/vBvariables/0/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/token_and_position_embedding_2/embedding_5/embeddings/vBvariables/1/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE>Adam/transformer_block_2/multi_head_attention_2/query/kernel/vBvariables/2/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/query/bias/vBvariables/3/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/key/kernel/vBvariables/4/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE:Adam/transformer_block_2/multi_head_attention_2/key/bias/vBvariables/5/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE>Adam/transformer_block_2/multi_head_attention_2/value/kernel/vBvariables/6/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE<Adam/transformer_block_2/multi_head_attention_2/value/bias/vBvariables/7/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUEIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/vBvariables/8/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUEGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/vBvariables/9/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
rl
VARIABLE_VALUEAdam/dense_8/kernel/vCvariables/10/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUEAdam/dense_8/bias/vCvariables/11/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
rl
VARIABLE_VALUEAdam/dense_9/kernel/vCvariables/12/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
pj
VARIABLE_VALUEAdam/dense_9/bias/vCvariables/13/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE6Adam/transformer_block_2/layer_normalization_4/gamma/vCvariables/14/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE5Adam/transformer_block_2/layer_normalization_4/beta/vCvariables/15/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE6Adam/transformer_block_2/layer_normalization_5/gamma/vCvariables/16/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
��
VARIABLE_VALUE5Adam/transformer_block_2/layer_normalization_5/beta/vCvariables/17/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUE*
O
saver_filenamePlaceholder*
_output_shapes
: *
dtype0*
shape: 
�&
StatefulPartitionedCall_1StatefulPartitionedCallsaver_filename#dense_10/kernel/Read/ReadVariableOp!dense_10/bias/Read/ReadVariableOp#dense_11/kernel/Read/ReadVariableOp!dense_11/bias/Read/ReadVariableOpItoken_and_position_embedding_2/embedding_4/embeddings/Read/ReadVariableOpItoken_and_position_embedding_2/embedding_5/embeddings/Read/ReadVariableOpKtransformer_block_2/multi_head_attention_2/query/kernel/Read/ReadVariableOpItransformer_block_2/multi_head_attention_2/query/bias/Read/ReadVariableOpItransformer_block_2/multi_head_attention_2/key/kernel/Read/ReadVariableOpGtransformer_block_2/multi_head_attention_2/key/bias/Read/ReadVariableOpKtransformer_block_2/multi_head_attention_2/value/kernel/Read/ReadVariableOpItransformer_block_2/multi_head_attention_2/value/bias/Read/ReadVariableOpVtransformer_block_2/multi_head_attention_2/attention_output/kernel/Read/ReadVariableOpTtransformer_block_2/multi_head_attention_2/attention_output/bias/Read/ReadVariableOp"dense_8/kernel/Read/ReadVariableOp dense_8/bias/Read/ReadVariableOp"dense_9/kernel/Read/ReadVariableOp dense_9/bias/Read/ReadVariableOpCtransformer_block_2/layer_normalization_4/gamma/Read/ReadVariableOpBtransformer_block_2/layer_normalization_4/beta/Read/ReadVariableOpCtransformer_block_2/layer_normalization_5/gamma/Read/ReadVariableOpBtransformer_block_2/layer_normalization_5/beta/Read/ReadVariableOpAdam/iter/Read/ReadVariableOpAdam/beta_1/Read/ReadVariableOpAdam/beta_2/Read/ReadVariableOpAdam/decay/Read/ReadVariableOp&Adam/learning_rate/Read/ReadVariableOptotal_1/Read/ReadVariableOpcount_1/Read/ReadVariableOptotal/Read/ReadVariableOpcount/Read/ReadVariableOp*Adam/dense_10/kernel/m/Read/ReadVariableOp(Adam/dense_10/bias/m/Read/ReadVariableOp*Adam/dense_11/kernel/m/Read/ReadVariableOp(Adam/dense_11/bias/m/Read/ReadVariableOpPAdam/token_and_position_embedding_2/embedding_4/embeddings/m/Read/ReadVariableOpPAdam/token_and_position_embedding_2/embedding_5/embeddings/m/Read/ReadVariableOpRAdam/transformer_block_2/multi_head_attention_2/query/kernel/m/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/query/bias/m/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/key/kernel/m/Read/ReadVariableOpNAdam/transformer_block_2/multi_head_attention_2/key/bias/m/Read/ReadVariableOpRAdam/transformer_block_2/multi_head_attention_2/value/kernel/m/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/value/bias/m/Read/ReadVariableOp]Adam/transformer_block_2/multi_head_attention_2/attention_output/kernel/m/Read/ReadVariableOp[Adam/transformer_block_2/multi_head_attention_2/attention_output/bias/m/Read/ReadVariableOp)Adam/dense_8/kernel/m/Read/ReadVariableOp'Adam/dense_8/bias/m/Read/ReadVariableOp)Adam/dense_9/kernel/m/Read/ReadVariableOp'Adam/dense_9/bias/m/Read/ReadVariableOpJAdam/transformer_block_2/layer_normalization_4/gamma/m/Read/ReadVariableOpIAdam/transformer_block_2/layer_normalization_4/beta/m/Read/ReadVariableOpJAdam/transformer_block_2/layer_normalization_5/gamma/m/Read/ReadVariableOpIAdam/transformer_block_2/layer_normalization_5/beta/m/Read/ReadVariableOp*Adam/dense_10/kernel/v/Read/ReadVariableOp(Adam/dense_10/bias/v/Read/ReadVariableOp*Adam/dense_11/kernel/v/Read/ReadVariableOp(Adam/dense_11/bias/v/Read/ReadVariableOpPAdam/token_and_position_embedding_2/embedding_4/embeddings/v/Read/ReadVariableOpPAdam/token_and_position_embedding_2/embedding_5/embeddings/v/Read/ReadVariableOpRAdam/transformer_block_2/multi_head_attention_2/query/kernel/v/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/query/bias/v/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/key/kernel/v/Read/ReadVariableOpNAdam/transformer_block_2/multi_head_attention_2/key/bias/v/Read/ReadVariableOpRAdam/transformer_block_2/multi_head_attention_2/value/kernel/v/Read/ReadVariableOpPAdam/transformer_block_2/multi_head_attention_2/value/bias/v/Read/ReadVariableOp]Adam/transformer_block_2/multi_head_attention_2/attention_output/kernel/v/Read/ReadVariableOp[Adam/transformer_block_2/multi_head_attention_2/attention_output/bias/v/Read/ReadVariableOp)Adam/dense_8/kernel/v/Read/ReadVariableOp'Adam/dense_8/bias/v/Read/ReadVariableOp)Adam/dense_9/kernel/v/Read/ReadVariableOp'Adam/dense_9/bias/v/Read/ReadVariableOpJAdam/transformer_block_2/layer_normalization_4/gamma/v/Read/ReadVariableOpIAdam/transformer_block_2/layer_normalization_4/beta/v/Read/ReadVariableOpJAdam/transformer_block_2/layer_normalization_5/gamma/v/Read/ReadVariableOpIAdam/transformer_block_2/layer_normalization_5/beta/v/Read/ReadVariableOpConst*X
TinQ
O2M	*
Tout
2*
_collective_manager_ids
 *
_output_shapes
: * 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *'
f"R 
__inference__traced_save_55040
�
StatefulPartitionedCall_2StatefulPartitionedCallsaver_filenamedense_10/kerneldense_10/biasdense_11/kerneldense_11/bias5token_and_position_embedding_2/embedding_4/embeddings5token_and_position_embedding_2/embedding_5/embeddings7transformer_block_2/multi_head_attention_2/query/kernel5transformer_block_2/multi_head_attention_2/query/bias5transformer_block_2/multi_head_attention_2/key/kernel3transformer_block_2/multi_head_attention_2/key/bias7transformer_block_2/multi_head_attention_2/value/kernel5transformer_block_2/multi_head_attention_2/value/biasBtransformer_block_2/multi_head_attention_2/attention_output/kernel@transformer_block_2/multi_head_attention_2/attention_output/biasdense_8/kerneldense_8/biasdense_9/kerneldense_9/bias/transformer_block_2/layer_normalization_4/gamma.transformer_block_2/layer_normalization_4/beta/transformer_block_2/layer_normalization_5/gamma.transformer_block_2/layer_normalization_5/beta	Adam/iterAdam/beta_1Adam/beta_2
Adam/decayAdam/learning_ratetotal_1count_1totalcountAdam/dense_10/kernel/mAdam/dense_10/bias/mAdam/dense_11/kernel/mAdam/dense_11/bias/m<Adam/token_and_position_embedding_2/embedding_4/embeddings/m<Adam/token_and_position_embedding_2/embedding_5/embeddings/m>Adam/transformer_block_2/multi_head_attention_2/query/kernel/m<Adam/transformer_block_2/multi_head_attention_2/query/bias/m<Adam/transformer_block_2/multi_head_attention_2/key/kernel/m:Adam/transformer_block_2/multi_head_attention_2/key/bias/m>Adam/transformer_block_2/multi_head_attention_2/value/kernel/m<Adam/transformer_block_2/multi_head_attention_2/value/bias/mIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/mGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/mAdam/dense_8/kernel/mAdam/dense_8/bias/mAdam/dense_9/kernel/mAdam/dense_9/bias/m6Adam/transformer_block_2/layer_normalization_4/gamma/m5Adam/transformer_block_2/layer_normalization_4/beta/m6Adam/transformer_block_2/layer_normalization_5/gamma/m5Adam/transformer_block_2/layer_normalization_5/beta/mAdam/dense_10/kernel/vAdam/dense_10/bias/vAdam/dense_11/kernel/vAdam/dense_11/bias/v<Adam/token_and_position_embedding_2/embedding_4/embeddings/v<Adam/token_and_position_embedding_2/embedding_5/embeddings/v>Adam/transformer_block_2/multi_head_attention_2/query/kernel/v<Adam/transformer_block_2/multi_head_attention_2/query/bias/v<Adam/transformer_block_2/multi_head_attention_2/key/kernel/v:Adam/transformer_block_2/multi_head_attention_2/key/bias/v>Adam/transformer_block_2/multi_head_attention_2/value/kernel/v<Adam/transformer_block_2/multi_head_attention_2/value/bias/vIAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/vGAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/vAdam/dense_8/kernel/vAdam/dense_8/bias/vAdam/dense_9/kernel/vAdam/dense_9/bias/v6Adam/transformer_block_2/layer_normalization_4/gamma/v5Adam/transformer_block_2/layer_normalization_4/beta/v6Adam/transformer_block_2/layer_normalization_5/gamma/v5Adam/transformer_block_2/layer_normalization_5/beta/v*W
TinP
N2L*
Tout
2*
_collective_manager_ids
 *
_output_shapes
: * 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� **
f%R#
!__inference__traced_restore_55275��
�
�
'__inference_dense_9_layer_call_fn_54762

inputs
unknown:
	unknown_0:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_9_layer_call_and_return_conditional_losses_52552s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
��
�:
!__inference__traced_restore_55275
file_prefix2
 assignvariableop_dense_10_kernel:.
 assignvariableop_1_dense_10_bias:4
"assignvariableop_2_dense_11_kernel:.
 assignvariableop_3_dense_11_bias:[
Hassignvariableop_4_token_and_position_embedding_2_embedding_4_embeddings:	�Z
Hassignvariableop_5_token_and_position_embedding_2_embedding_5_embeddings:d`
Jassignvariableop_6_transformer_block_2_multi_head_attention_2_query_kernel:Z
Hassignvariableop_7_transformer_block_2_multi_head_attention_2_query_bias:^
Hassignvariableop_8_transformer_block_2_multi_head_attention_2_key_kernel:X
Fassignvariableop_9_transformer_block_2_multi_head_attention_2_key_bias:a
Kassignvariableop_10_transformer_block_2_multi_head_attention_2_value_kernel:[
Iassignvariableop_11_transformer_block_2_multi_head_attention_2_value_bias:l
Vassignvariableop_12_transformer_block_2_multi_head_attention_2_attention_output_kernel:b
Tassignvariableop_13_transformer_block_2_multi_head_attention_2_attention_output_bias:4
"assignvariableop_14_dense_8_kernel:.
 assignvariableop_15_dense_8_bias:4
"assignvariableop_16_dense_9_kernel:.
 assignvariableop_17_dense_9_bias:Q
Cassignvariableop_18_transformer_block_2_layer_normalization_4_gamma:P
Bassignvariableop_19_transformer_block_2_layer_normalization_4_beta:Q
Cassignvariableop_20_transformer_block_2_layer_normalization_5_gamma:P
Bassignvariableop_21_transformer_block_2_layer_normalization_5_beta:'
assignvariableop_22_adam_iter:	 )
assignvariableop_23_adam_beta_1: )
assignvariableop_24_adam_beta_2: (
assignvariableop_25_adam_decay: 0
&assignvariableop_26_adam_learning_rate: %
assignvariableop_27_total_1: %
assignvariableop_28_count_1: #
assignvariableop_29_total: #
assignvariableop_30_count: <
*assignvariableop_31_adam_dense_10_kernel_m:6
(assignvariableop_32_adam_dense_10_bias_m:<
*assignvariableop_33_adam_dense_11_kernel_m:6
(assignvariableop_34_adam_dense_11_bias_m:c
Passignvariableop_35_adam_token_and_position_embedding_2_embedding_4_embeddings_m:	�b
Passignvariableop_36_adam_token_and_position_embedding_2_embedding_5_embeddings_m:dh
Rassignvariableop_37_adam_transformer_block_2_multi_head_attention_2_query_kernel_m:b
Passignvariableop_38_adam_transformer_block_2_multi_head_attention_2_query_bias_m:f
Passignvariableop_39_adam_transformer_block_2_multi_head_attention_2_key_kernel_m:`
Nassignvariableop_40_adam_transformer_block_2_multi_head_attention_2_key_bias_m:h
Rassignvariableop_41_adam_transformer_block_2_multi_head_attention_2_value_kernel_m:b
Passignvariableop_42_adam_transformer_block_2_multi_head_attention_2_value_bias_m:s
]assignvariableop_43_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_m:i
[assignvariableop_44_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_m:;
)assignvariableop_45_adam_dense_8_kernel_m:5
'assignvariableop_46_adam_dense_8_bias_m:;
)assignvariableop_47_adam_dense_9_kernel_m:5
'assignvariableop_48_adam_dense_9_bias_m:X
Jassignvariableop_49_adam_transformer_block_2_layer_normalization_4_gamma_m:W
Iassignvariableop_50_adam_transformer_block_2_layer_normalization_4_beta_m:X
Jassignvariableop_51_adam_transformer_block_2_layer_normalization_5_gamma_m:W
Iassignvariableop_52_adam_transformer_block_2_layer_normalization_5_beta_m:<
*assignvariableop_53_adam_dense_10_kernel_v:6
(assignvariableop_54_adam_dense_10_bias_v:<
*assignvariableop_55_adam_dense_11_kernel_v:6
(assignvariableop_56_adam_dense_11_bias_v:c
Passignvariableop_57_adam_token_and_position_embedding_2_embedding_4_embeddings_v:	�b
Passignvariableop_58_adam_token_and_position_embedding_2_embedding_5_embeddings_v:dh
Rassignvariableop_59_adam_transformer_block_2_multi_head_attention_2_query_kernel_v:b
Passignvariableop_60_adam_transformer_block_2_multi_head_attention_2_query_bias_v:f
Passignvariableop_61_adam_transformer_block_2_multi_head_attention_2_key_kernel_v:`
Nassignvariableop_62_adam_transformer_block_2_multi_head_attention_2_key_bias_v:h
Rassignvariableop_63_adam_transformer_block_2_multi_head_attention_2_value_kernel_v:b
Passignvariableop_64_adam_transformer_block_2_multi_head_attention_2_value_bias_v:s
]assignvariableop_65_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_v:i
[assignvariableop_66_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_v:;
)assignvariableop_67_adam_dense_8_kernel_v:5
'assignvariableop_68_adam_dense_8_bias_v:;
)assignvariableop_69_adam_dense_9_kernel_v:5
'assignvariableop_70_adam_dense_9_bias_v:X
Jassignvariableop_71_adam_transformer_block_2_layer_normalization_4_gamma_v:W
Iassignvariableop_72_adam_transformer_block_2_layer_normalization_4_beta_v:X
Jassignvariableop_73_adam_transformer_block_2_layer_normalization_5_gamma_v:W
Iassignvariableop_74_adam_transformer_block_2_layer_normalization_5_beta_v:
identity_76��AssignVariableOp�AssignVariableOp_1�AssignVariableOp_10�AssignVariableOp_11�AssignVariableOp_12�AssignVariableOp_13�AssignVariableOp_14�AssignVariableOp_15�AssignVariableOp_16�AssignVariableOp_17�AssignVariableOp_18�AssignVariableOp_19�AssignVariableOp_2�AssignVariableOp_20�AssignVariableOp_21�AssignVariableOp_22�AssignVariableOp_23�AssignVariableOp_24�AssignVariableOp_25�AssignVariableOp_26�AssignVariableOp_27�AssignVariableOp_28�AssignVariableOp_29�AssignVariableOp_3�AssignVariableOp_30�AssignVariableOp_31�AssignVariableOp_32�AssignVariableOp_33�AssignVariableOp_34�AssignVariableOp_35�AssignVariableOp_36�AssignVariableOp_37�AssignVariableOp_38�AssignVariableOp_39�AssignVariableOp_4�AssignVariableOp_40�AssignVariableOp_41�AssignVariableOp_42�AssignVariableOp_43�AssignVariableOp_44�AssignVariableOp_45�AssignVariableOp_46�AssignVariableOp_47�AssignVariableOp_48�AssignVariableOp_49�AssignVariableOp_5�AssignVariableOp_50�AssignVariableOp_51�AssignVariableOp_52�AssignVariableOp_53�AssignVariableOp_54�AssignVariableOp_55�AssignVariableOp_56�AssignVariableOp_57�AssignVariableOp_58�AssignVariableOp_59�AssignVariableOp_6�AssignVariableOp_60�AssignVariableOp_61�AssignVariableOp_62�AssignVariableOp_63�AssignVariableOp_64�AssignVariableOp_65�AssignVariableOp_66�AssignVariableOp_67�AssignVariableOp_68�AssignVariableOp_69�AssignVariableOp_7�AssignVariableOp_70�AssignVariableOp_71�AssignVariableOp_72�AssignVariableOp_73�AssignVariableOp_74�AssignVariableOp_8�AssignVariableOp_9�$
RestoreV2/tensor_namesConst"/device:CPU:0*
_output_shapes
:L*
dtype0*�#
value�#B�#LB6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUEB&variables/0/.ATTRIBUTES/VARIABLE_VALUEB&variables/1/.ATTRIBUTES/VARIABLE_VALUEB&variables/2/.ATTRIBUTES/VARIABLE_VALUEB&variables/3/.ATTRIBUTES/VARIABLE_VALUEB&variables/4/.ATTRIBUTES/VARIABLE_VALUEB&variables/5/.ATTRIBUTES/VARIABLE_VALUEB&variables/6/.ATTRIBUTES/VARIABLE_VALUEB&variables/7/.ATTRIBUTES/VARIABLE_VALUEB&variables/8/.ATTRIBUTES/VARIABLE_VALUEB&variables/9/.ATTRIBUTES/VARIABLE_VALUEB'variables/10/.ATTRIBUTES/VARIABLE_VALUEB'variables/11/.ATTRIBUTES/VARIABLE_VALUEB'variables/12/.ATTRIBUTES/VARIABLE_VALUEB'variables/13/.ATTRIBUTES/VARIABLE_VALUEB'variables/14/.ATTRIBUTES/VARIABLE_VALUEB'variables/15/.ATTRIBUTES/VARIABLE_VALUEB'variables/16/.ATTRIBUTES/VARIABLE_VALUEB'variables/17/.ATTRIBUTES/VARIABLE_VALUEB)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUEB*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUEB2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/0/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/1/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/2/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/3/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/4/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/5/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/6/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/7/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/8/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/9/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/10/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/11/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/12/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/13/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/14/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/15/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/16/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/17/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/0/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/1/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/2/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/3/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/4/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/5/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/6/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/7/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/8/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/9/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/10/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/11/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/12/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/13/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/14/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/15/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/16/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/17/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEB_CHECKPOINTABLE_OBJECT_GRAPH�
RestoreV2/shape_and_slicesConst"/device:CPU:0*
_output_shapes
:L*
dtype0*�
value�B�LB B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B �
	RestoreV2	RestoreV2file_prefixRestoreV2/tensor_names:output:0#RestoreV2/shape_and_slices:output:0"/device:CPU:0*�
_output_shapes�
�::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*Z
dtypesP
N2L	[
IdentityIdentityRestoreV2:tensors:0"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOpAssignVariableOp assignvariableop_dense_10_kernelIdentity:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_1IdentityRestoreV2:tensors:1"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_1AssignVariableOp assignvariableop_1_dense_10_biasIdentity_1:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_2IdentityRestoreV2:tensors:2"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_2AssignVariableOp"assignvariableop_2_dense_11_kernelIdentity_2:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_3IdentityRestoreV2:tensors:3"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_3AssignVariableOp assignvariableop_3_dense_11_biasIdentity_3:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_4IdentityRestoreV2:tensors:4"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_4AssignVariableOpHassignvariableop_4_token_and_position_embedding_2_embedding_4_embeddingsIdentity_4:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_5IdentityRestoreV2:tensors:5"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_5AssignVariableOpHassignvariableop_5_token_and_position_embedding_2_embedding_5_embeddingsIdentity_5:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_6IdentityRestoreV2:tensors:6"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_6AssignVariableOpJassignvariableop_6_transformer_block_2_multi_head_attention_2_query_kernelIdentity_6:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_7IdentityRestoreV2:tensors:7"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_7AssignVariableOpHassignvariableop_7_transformer_block_2_multi_head_attention_2_query_biasIdentity_7:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_8IdentityRestoreV2:tensors:8"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_8AssignVariableOpHassignvariableop_8_transformer_block_2_multi_head_attention_2_key_kernelIdentity_8:output:0"/device:CPU:0*
_output_shapes
 *
dtype0]

Identity_9IdentityRestoreV2:tensors:9"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_9AssignVariableOpFassignvariableop_9_transformer_block_2_multi_head_attention_2_key_biasIdentity_9:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_10IdentityRestoreV2:tensors:10"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_10AssignVariableOpKassignvariableop_10_transformer_block_2_multi_head_attention_2_value_kernelIdentity_10:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_11IdentityRestoreV2:tensors:11"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_11AssignVariableOpIassignvariableop_11_transformer_block_2_multi_head_attention_2_value_biasIdentity_11:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_12IdentityRestoreV2:tensors:12"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_12AssignVariableOpVassignvariableop_12_transformer_block_2_multi_head_attention_2_attention_output_kernelIdentity_12:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_13IdentityRestoreV2:tensors:13"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_13AssignVariableOpTassignvariableop_13_transformer_block_2_multi_head_attention_2_attention_output_biasIdentity_13:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_14IdentityRestoreV2:tensors:14"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_14AssignVariableOp"assignvariableop_14_dense_8_kernelIdentity_14:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_15IdentityRestoreV2:tensors:15"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_15AssignVariableOp assignvariableop_15_dense_8_biasIdentity_15:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_16IdentityRestoreV2:tensors:16"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_16AssignVariableOp"assignvariableop_16_dense_9_kernelIdentity_16:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_17IdentityRestoreV2:tensors:17"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_17AssignVariableOp assignvariableop_17_dense_9_biasIdentity_17:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_18IdentityRestoreV2:tensors:18"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_18AssignVariableOpCassignvariableop_18_transformer_block_2_layer_normalization_4_gammaIdentity_18:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_19IdentityRestoreV2:tensors:19"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_19AssignVariableOpBassignvariableop_19_transformer_block_2_layer_normalization_4_betaIdentity_19:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_20IdentityRestoreV2:tensors:20"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_20AssignVariableOpCassignvariableop_20_transformer_block_2_layer_normalization_5_gammaIdentity_20:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_21IdentityRestoreV2:tensors:21"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_21AssignVariableOpBassignvariableop_21_transformer_block_2_layer_normalization_5_betaIdentity_21:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_22IdentityRestoreV2:tensors:22"/device:CPU:0*
T0	*
_output_shapes
:�
AssignVariableOp_22AssignVariableOpassignvariableop_22_adam_iterIdentity_22:output:0"/device:CPU:0*
_output_shapes
 *
dtype0	_
Identity_23IdentityRestoreV2:tensors:23"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_23AssignVariableOpassignvariableop_23_adam_beta_1Identity_23:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_24IdentityRestoreV2:tensors:24"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_24AssignVariableOpassignvariableop_24_adam_beta_2Identity_24:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_25IdentityRestoreV2:tensors:25"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_25AssignVariableOpassignvariableop_25_adam_decayIdentity_25:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_26IdentityRestoreV2:tensors:26"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_26AssignVariableOp&assignvariableop_26_adam_learning_rateIdentity_26:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_27IdentityRestoreV2:tensors:27"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_27AssignVariableOpassignvariableop_27_total_1Identity_27:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_28IdentityRestoreV2:tensors:28"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_28AssignVariableOpassignvariableop_28_count_1Identity_28:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_29IdentityRestoreV2:tensors:29"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_29AssignVariableOpassignvariableop_29_totalIdentity_29:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_30IdentityRestoreV2:tensors:30"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_30AssignVariableOpassignvariableop_30_countIdentity_30:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_31IdentityRestoreV2:tensors:31"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_31AssignVariableOp*assignvariableop_31_adam_dense_10_kernel_mIdentity_31:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_32IdentityRestoreV2:tensors:32"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_32AssignVariableOp(assignvariableop_32_adam_dense_10_bias_mIdentity_32:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_33IdentityRestoreV2:tensors:33"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_33AssignVariableOp*assignvariableop_33_adam_dense_11_kernel_mIdentity_33:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_34IdentityRestoreV2:tensors:34"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_34AssignVariableOp(assignvariableop_34_adam_dense_11_bias_mIdentity_34:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_35IdentityRestoreV2:tensors:35"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_35AssignVariableOpPassignvariableop_35_adam_token_and_position_embedding_2_embedding_4_embeddings_mIdentity_35:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_36IdentityRestoreV2:tensors:36"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_36AssignVariableOpPassignvariableop_36_adam_token_and_position_embedding_2_embedding_5_embeddings_mIdentity_36:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_37IdentityRestoreV2:tensors:37"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_37AssignVariableOpRassignvariableop_37_adam_transformer_block_2_multi_head_attention_2_query_kernel_mIdentity_37:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_38IdentityRestoreV2:tensors:38"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_38AssignVariableOpPassignvariableop_38_adam_transformer_block_2_multi_head_attention_2_query_bias_mIdentity_38:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_39IdentityRestoreV2:tensors:39"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_39AssignVariableOpPassignvariableop_39_adam_transformer_block_2_multi_head_attention_2_key_kernel_mIdentity_39:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_40IdentityRestoreV2:tensors:40"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_40AssignVariableOpNassignvariableop_40_adam_transformer_block_2_multi_head_attention_2_key_bias_mIdentity_40:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_41IdentityRestoreV2:tensors:41"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_41AssignVariableOpRassignvariableop_41_adam_transformer_block_2_multi_head_attention_2_value_kernel_mIdentity_41:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_42IdentityRestoreV2:tensors:42"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_42AssignVariableOpPassignvariableop_42_adam_transformer_block_2_multi_head_attention_2_value_bias_mIdentity_42:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_43IdentityRestoreV2:tensors:43"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_43AssignVariableOp]assignvariableop_43_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_mIdentity_43:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_44IdentityRestoreV2:tensors:44"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_44AssignVariableOp[assignvariableop_44_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_mIdentity_44:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_45IdentityRestoreV2:tensors:45"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_45AssignVariableOp)assignvariableop_45_adam_dense_8_kernel_mIdentity_45:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_46IdentityRestoreV2:tensors:46"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_46AssignVariableOp'assignvariableop_46_adam_dense_8_bias_mIdentity_46:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_47IdentityRestoreV2:tensors:47"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_47AssignVariableOp)assignvariableop_47_adam_dense_9_kernel_mIdentity_47:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_48IdentityRestoreV2:tensors:48"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_48AssignVariableOp'assignvariableop_48_adam_dense_9_bias_mIdentity_48:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_49IdentityRestoreV2:tensors:49"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_49AssignVariableOpJassignvariableop_49_adam_transformer_block_2_layer_normalization_4_gamma_mIdentity_49:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_50IdentityRestoreV2:tensors:50"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_50AssignVariableOpIassignvariableop_50_adam_transformer_block_2_layer_normalization_4_beta_mIdentity_50:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_51IdentityRestoreV2:tensors:51"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_51AssignVariableOpJassignvariableop_51_adam_transformer_block_2_layer_normalization_5_gamma_mIdentity_51:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_52IdentityRestoreV2:tensors:52"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_52AssignVariableOpIassignvariableop_52_adam_transformer_block_2_layer_normalization_5_beta_mIdentity_52:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_53IdentityRestoreV2:tensors:53"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_53AssignVariableOp*assignvariableop_53_adam_dense_10_kernel_vIdentity_53:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_54IdentityRestoreV2:tensors:54"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_54AssignVariableOp(assignvariableop_54_adam_dense_10_bias_vIdentity_54:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_55IdentityRestoreV2:tensors:55"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_55AssignVariableOp*assignvariableop_55_adam_dense_11_kernel_vIdentity_55:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_56IdentityRestoreV2:tensors:56"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_56AssignVariableOp(assignvariableop_56_adam_dense_11_bias_vIdentity_56:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_57IdentityRestoreV2:tensors:57"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_57AssignVariableOpPassignvariableop_57_adam_token_and_position_embedding_2_embedding_4_embeddings_vIdentity_57:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_58IdentityRestoreV2:tensors:58"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_58AssignVariableOpPassignvariableop_58_adam_token_and_position_embedding_2_embedding_5_embeddings_vIdentity_58:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_59IdentityRestoreV2:tensors:59"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_59AssignVariableOpRassignvariableop_59_adam_transformer_block_2_multi_head_attention_2_query_kernel_vIdentity_59:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_60IdentityRestoreV2:tensors:60"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_60AssignVariableOpPassignvariableop_60_adam_transformer_block_2_multi_head_attention_2_query_bias_vIdentity_60:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_61IdentityRestoreV2:tensors:61"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_61AssignVariableOpPassignvariableop_61_adam_transformer_block_2_multi_head_attention_2_key_kernel_vIdentity_61:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_62IdentityRestoreV2:tensors:62"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_62AssignVariableOpNassignvariableop_62_adam_transformer_block_2_multi_head_attention_2_key_bias_vIdentity_62:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_63IdentityRestoreV2:tensors:63"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_63AssignVariableOpRassignvariableop_63_adam_transformer_block_2_multi_head_attention_2_value_kernel_vIdentity_63:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_64IdentityRestoreV2:tensors:64"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_64AssignVariableOpPassignvariableop_64_adam_transformer_block_2_multi_head_attention_2_value_bias_vIdentity_64:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_65IdentityRestoreV2:tensors:65"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_65AssignVariableOp]assignvariableop_65_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_vIdentity_65:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_66IdentityRestoreV2:tensors:66"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_66AssignVariableOp[assignvariableop_66_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_vIdentity_66:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_67IdentityRestoreV2:tensors:67"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_67AssignVariableOp)assignvariableop_67_adam_dense_8_kernel_vIdentity_67:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_68IdentityRestoreV2:tensors:68"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_68AssignVariableOp'assignvariableop_68_adam_dense_8_bias_vIdentity_68:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_69IdentityRestoreV2:tensors:69"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_69AssignVariableOp)assignvariableop_69_adam_dense_9_kernel_vIdentity_69:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_70IdentityRestoreV2:tensors:70"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_70AssignVariableOp'assignvariableop_70_adam_dense_9_bias_vIdentity_70:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_71IdentityRestoreV2:tensors:71"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_71AssignVariableOpJassignvariableop_71_adam_transformer_block_2_layer_normalization_4_gamma_vIdentity_71:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_72IdentityRestoreV2:tensors:72"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_72AssignVariableOpIassignvariableop_72_adam_transformer_block_2_layer_normalization_4_beta_vIdentity_72:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_73IdentityRestoreV2:tensors:73"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_73AssignVariableOpJassignvariableop_73_adam_transformer_block_2_layer_normalization_5_gamma_vIdentity_73:output:0"/device:CPU:0*
_output_shapes
 *
dtype0_
Identity_74IdentityRestoreV2:tensors:74"/device:CPU:0*
T0*
_output_shapes
:�
AssignVariableOp_74AssignVariableOpIassignvariableop_74_adam_transformer_block_2_layer_normalization_5_beta_vIdentity_74:output:0"/device:CPU:0*
_output_shapes
 *
dtype01
NoOpNoOp"/device:CPU:0*
_output_shapes
 �
Identity_75Identityfile_prefix^AssignVariableOp^AssignVariableOp_1^AssignVariableOp_10^AssignVariableOp_11^AssignVariableOp_12^AssignVariableOp_13^AssignVariableOp_14^AssignVariableOp_15^AssignVariableOp_16^AssignVariableOp_17^AssignVariableOp_18^AssignVariableOp_19^AssignVariableOp_2^AssignVariableOp_20^AssignVariableOp_21^AssignVariableOp_22^AssignVariableOp_23^AssignVariableOp_24^AssignVariableOp_25^AssignVariableOp_26^AssignVariableOp_27^AssignVariableOp_28^AssignVariableOp_29^AssignVariableOp_3^AssignVariableOp_30^AssignVariableOp_31^AssignVariableOp_32^AssignVariableOp_33^AssignVariableOp_34^AssignVariableOp_35^AssignVariableOp_36^AssignVariableOp_37^AssignVariableOp_38^AssignVariableOp_39^AssignVariableOp_4^AssignVariableOp_40^AssignVariableOp_41^AssignVariableOp_42^AssignVariableOp_43^AssignVariableOp_44^AssignVariableOp_45^AssignVariableOp_46^AssignVariableOp_47^AssignVariableOp_48^AssignVariableOp_49^AssignVariableOp_5^AssignVariableOp_50^AssignVariableOp_51^AssignVariableOp_52^AssignVariableOp_53^AssignVariableOp_54^AssignVariableOp_55^AssignVariableOp_56^AssignVariableOp_57^AssignVariableOp_58^AssignVariableOp_59^AssignVariableOp_6^AssignVariableOp_60^AssignVariableOp_61^AssignVariableOp_62^AssignVariableOp_63^AssignVariableOp_64^AssignVariableOp_65^AssignVariableOp_66^AssignVariableOp_67^AssignVariableOp_68^AssignVariableOp_69^AssignVariableOp_7^AssignVariableOp_70^AssignVariableOp_71^AssignVariableOp_72^AssignVariableOp_73^AssignVariableOp_74^AssignVariableOp_8^AssignVariableOp_9^NoOp"/device:CPU:0*
T0*
_output_shapes
: W
Identity_76IdentityIdentity_75:output:0^NoOp_1*
T0*
_output_shapes
: �
NoOp_1NoOp^AssignVariableOp^AssignVariableOp_1^AssignVariableOp_10^AssignVariableOp_11^AssignVariableOp_12^AssignVariableOp_13^AssignVariableOp_14^AssignVariableOp_15^AssignVariableOp_16^AssignVariableOp_17^AssignVariableOp_18^AssignVariableOp_19^AssignVariableOp_2^AssignVariableOp_20^AssignVariableOp_21^AssignVariableOp_22^AssignVariableOp_23^AssignVariableOp_24^AssignVariableOp_25^AssignVariableOp_26^AssignVariableOp_27^AssignVariableOp_28^AssignVariableOp_29^AssignVariableOp_3^AssignVariableOp_30^AssignVariableOp_31^AssignVariableOp_32^AssignVariableOp_33^AssignVariableOp_34^AssignVariableOp_35^AssignVariableOp_36^AssignVariableOp_37^AssignVariableOp_38^AssignVariableOp_39^AssignVariableOp_4^AssignVariableOp_40^AssignVariableOp_41^AssignVariableOp_42^AssignVariableOp_43^AssignVariableOp_44^AssignVariableOp_45^AssignVariableOp_46^AssignVariableOp_47^AssignVariableOp_48^AssignVariableOp_49^AssignVariableOp_5^AssignVariableOp_50^AssignVariableOp_51^AssignVariableOp_52^AssignVariableOp_53^AssignVariableOp_54^AssignVariableOp_55^AssignVariableOp_56^AssignVariableOp_57^AssignVariableOp_58^AssignVariableOp_59^AssignVariableOp_6^AssignVariableOp_60^AssignVariableOp_61^AssignVariableOp_62^AssignVariableOp_63^AssignVariableOp_64^AssignVariableOp_65^AssignVariableOp_66^AssignVariableOp_67^AssignVariableOp_68^AssignVariableOp_69^AssignVariableOp_7^AssignVariableOp_70^AssignVariableOp_71^AssignVariableOp_72^AssignVariableOp_73^AssignVariableOp_74^AssignVariableOp_8^AssignVariableOp_9*"
_acd_function_control_output(*
_output_shapes
 "#
identity_76Identity_76:output:0*�
_input_shapes�
�: : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 2$
AssignVariableOpAssignVariableOp2(
AssignVariableOp_1AssignVariableOp_12*
AssignVariableOp_10AssignVariableOp_102*
AssignVariableOp_11AssignVariableOp_112*
AssignVariableOp_12AssignVariableOp_122*
AssignVariableOp_13AssignVariableOp_132*
AssignVariableOp_14AssignVariableOp_142*
AssignVariableOp_15AssignVariableOp_152*
AssignVariableOp_16AssignVariableOp_162*
AssignVariableOp_17AssignVariableOp_172*
AssignVariableOp_18AssignVariableOp_182*
AssignVariableOp_19AssignVariableOp_192(
AssignVariableOp_2AssignVariableOp_22*
AssignVariableOp_20AssignVariableOp_202*
AssignVariableOp_21AssignVariableOp_212*
AssignVariableOp_22AssignVariableOp_222*
AssignVariableOp_23AssignVariableOp_232*
AssignVariableOp_24AssignVariableOp_242*
AssignVariableOp_25AssignVariableOp_252*
AssignVariableOp_26AssignVariableOp_262*
AssignVariableOp_27AssignVariableOp_272*
AssignVariableOp_28AssignVariableOp_282*
AssignVariableOp_29AssignVariableOp_292(
AssignVariableOp_3AssignVariableOp_32*
AssignVariableOp_30AssignVariableOp_302*
AssignVariableOp_31AssignVariableOp_312*
AssignVariableOp_32AssignVariableOp_322*
AssignVariableOp_33AssignVariableOp_332*
AssignVariableOp_34AssignVariableOp_342*
AssignVariableOp_35AssignVariableOp_352*
AssignVariableOp_36AssignVariableOp_362*
AssignVariableOp_37AssignVariableOp_372*
AssignVariableOp_38AssignVariableOp_382*
AssignVariableOp_39AssignVariableOp_392(
AssignVariableOp_4AssignVariableOp_42*
AssignVariableOp_40AssignVariableOp_402*
AssignVariableOp_41AssignVariableOp_412*
AssignVariableOp_42AssignVariableOp_422*
AssignVariableOp_43AssignVariableOp_432*
AssignVariableOp_44AssignVariableOp_442*
AssignVariableOp_45AssignVariableOp_452*
AssignVariableOp_46AssignVariableOp_462*
AssignVariableOp_47AssignVariableOp_472*
AssignVariableOp_48AssignVariableOp_482*
AssignVariableOp_49AssignVariableOp_492(
AssignVariableOp_5AssignVariableOp_52*
AssignVariableOp_50AssignVariableOp_502*
AssignVariableOp_51AssignVariableOp_512*
AssignVariableOp_52AssignVariableOp_522*
AssignVariableOp_53AssignVariableOp_532*
AssignVariableOp_54AssignVariableOp_542*
AssignVariableOp_55AssignVariableOp_552*
AssignVariableOp_56AssignVariableOp_562*
AssignVariableOp_57AssignVariableOp_572*
AssignVariableOp_58AssignVariableOp_582*
AssignVariableOp_59AssignVariableOp_592(
AssignVariableOp_6AssignVariableOp_62*
AssignVariableOp_60AssignVariableOp_602*
AssignVariableOp_61AssignVariableOp_612*
AssignVariableOp_62AssignVariableOp_622*
AssignVariableOp_63AssignVariableOp_632*
AssignVariableOp_64AssignVariableOp_642*
AssignVariableOp_65AssignVariableOp_652*
AssignVariableOp_66AssignVariableOp_662*
AssignVariableOp_67AssignVariableOp_672*
AssignVariableOp_68AssignVariableOp_682*
AssignVariableOp_69AssignVariableOp_692(
AssignVariableOp_7AssignVariableOp_72*
AssignVariableOp_70AssignVariableOp_702*
AssignVariableOp_71AssignVariableOp_712*
AssignVariableOp_72AssignVariableOp_722*
AssignVariableOp_73AssignVariableOp_732*
AssignVariableOp_74AssignVariableOp_742(
AssignVariableOp_8AssignVariableOp_82(
AssignVariableOp_9AssignVariableOp_9:C ?

_output_shapes
: 
%
_user_specified_namefile_prefix
��
�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_53225

inputsX
Bmulti_head_attention_2_query_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_query_add_readvariableop_resource:V
@multi_head_attention_2_key_einsum_einsum_readvariableop_resource:H
6multi_head_attention_2_key_add_readvariableop_resource:X
Bmulti_head_attention_2_value_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_value_add_readvariableop_resource:c
Mmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:Q
Cmulti_head_attention_2_attention_output_add_readvariableop_resource:I
;layer_normalization_4_batchnorm_mul_readvariableop_resource:E
7layer_normalization_4_batchnorm_readvariableop_resource:H
6sequential_2_dense_8_tensordot_readvariableop_resource:B
4sequential_2_dense_8_biasadd_readvariableop_resource:H
6sequential_2_dense_9_tensordot_readvariableop_resource:B
4sequential_2_dense_9_biasadd_readvariableop_resource:I
;layer_normalization_5_batchnorm_mul_readvariableop_resource:E
7layer_normalization_5_batchnorm_readvariableop_resource:
identity��.layer_normalization_4/batchnorm/ReadVariableOp�2layer_normalization_4/batchnorm/mul/ReadVariableOp�.layer_normalization_5/batchnorm/ReadVariableOp�2layer_normalization_5/batchnorm/mul/ReadVariableOp�:multi_head_attention_2/attention_output/add/ReadVariableOp�Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�-multi_head_attention_2/key/add/ReadVariableOp�7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/query/add/ReadVariableOp�9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/value/add/ReadVariableOp�9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�+sequential_2/dense_8/BiasAdd/ReadVariableOp�-sequential_2/dense_8/Tensordot/ReadVariableOp�+sequential_2/dense_9/BiasAdd/ReadVariableOp�-sequential_2/dense_9/Tensordot/ReadVariableOp�
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/query/einsum/EinsumEinsuminputsAmulti_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/query/add/ReadVariableOpReadVariableOp8multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/query/addAddV23multi_head_attention_2/query/einsum/Einsum:output:07multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOp@multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
(multi_head_attention_2/key/einsum/EinsumEinsuminputs?multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
-multi_head_attention_2/key/add/ReadVariableOpReadVariableOp6multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
multi_head_attention_2/key/addAddV21multi_head_attention_2/key/einsum/Einsum:output:05multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/value/einsum/EinsumEinsuminputsAmulti_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/value/add/ReadVariableOpReadVariableOp8multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/value/addAddV23multi_head_attention_2/value/einsum/Einsum:output:07multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������da
multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
multi_head_attention_2/MulMul$multi_head_attention_2/query/add:z:0%multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
$multi_head_attention_2/einsum/EinsumEinsum"multi_head_attention_2/key/add:z:0multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
&multi_head_attention_2/softmax/SoftmaxSoftmax-multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
&multi_head_attention_2/einsum_1/EinsumEinsum0multi_head_attention_2/softmax/Softmax:softmax:0$multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpMmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
5multi_head_attention_2/attention_output/einsum/EinsumEinsum/multi_head_attention_2/einsum_1/Einsum:output:0Lmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
:multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpCmulti_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
+multi_head_attention_2/attention_output/addAddV2>multi_head_attention_2/attention_output/einsum/Einsum:output:0Bmulti_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d\
dropout_9/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_9/dropout/MulMul/multi_head_attention_2/attention_output/add:z:0 dropout_9/dropout/Const:output:0*
T0*+
_output_shapes
:���������dv
dropout_9/dropout/ShapeShape/multi_head_attention_2/attention_output/add:z:0*
T0*
_output_shapes
:�
.dropout_9/dropout/random_uniform/RandomUniformRandomUniform dropout_9/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0e
 dropout_9/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_9/dropout/GreaterEqualGreaterEqual7dropout_9/dropout/random_uniform/RandomUniform:output:0)dropout_9/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
dropout_9/dropout/CastCast"dropout_9/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
dropout_9/dropout/Mul_1Muldropout_9/dropout/Mul:z:0dropout_9/dropout/Cast:y:0*
T0*+
_output_shapes
:���������dg
addAddV2inputsdropout_9/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_4/moments/meanMeanadd:z:0=layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_4/moments/StopGradientStopGradient+layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_4/moments/SquaredDifferenceSquaredDifferenceadd:z:03layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_4/moments/varianceMean3layer_normalization_4/moments/SquaredDifference:z:0Alayer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_4/batchnorm/addAddV2/layer_normalization_4/moments/variance:output:0.layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/RsqrtRsqrt'layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/mulMul)layer_normalization_4/batchnorm/Rsqrt:y:0:layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_1Muladd:z:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_2Mul+layer_normalization_4/moments/mean:output:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_4/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/subSub6layer_normalization_4/batchnorm/ReadVariableOp:value:0)layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/add_1AddV2)layer_normalization_4/batchnorm/mul_1:z:0'layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       }
$sequential_2/dense_8/Tensordot/ShapeShape)layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:n
,sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/GatherV2GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/free:output:05sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_8/Tensordot/GatherV2_1GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/axes:output:07sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_8/Tensordot/ProdProd0sequential_2/dense_8/Tensordot/GatherV2:output:0-sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_8/Tensordot/Prod_1Prod2sequential_2/dense_8/Tensordot/GatherV2_1:output:0/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_8/Tensordot/concatConcatV2,sequential_2/dense_8/Tensordot/free:output:0,sequential_2/dense_8/Tensordot/axes:output:03sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_8/Tensordot/stackPack,sequential_2/dense_8/Tensordot/Prod:output:0.sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_8/Tensordot/transpose	Transpose)layer_normalization_4/batchnorm/add_1:z:0.sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_8/Tensordot/ReshapeReshape,sequential_2/dense_8/Tensordot/transpose:y:0-sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_8/Tensordot/MatMulMatMul/sequential_2/dense_8/Tensordot/Reshape:output:05sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/concat_1ConcatV20sequential_2/dense_8/Tensordot/GatherV2:output:0/sequential_2/dense_8/Tensordot/Const_2:output:05sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_8/TensordotReshape/sequential_2/dense_8/Tensordot/MatMul:product:00sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_8/BiasAddBiasAdd'sequential_2/dense_8/Tensordot:output:03sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d~
sequential_2/dense_8/ReluRelu%sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       {
$sequential_2/dense_9/Tensordot/ShapeShape'sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:n
,sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/GatherV2GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/free:output:05sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_9/Tensordot/GatherV2_1GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/axes:output:07sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_9/Tensordot/ProdProd0sequential_2/dense_9/Tensordot/GatherV2:output:0-sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_9/Tensordot/Prod_1Prod2sequential_2/dense_9/Tensordot/GatherV2_1:output:0/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_9/Tensordot/concatConcatV2,sequential_2/dense_9/Tensordot/free:output:0,sequential_2/dense_9/Tensordot/axes:output:03sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_9/Tensordot/stackPack,sequential_2/dense_9/Tensordot/Prod:output:0.sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_9/Tensordot/transpose	Transpose'sequential_2/dense_8/Relu:activations:0.sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_9/Tensordot/ReshapeReshape,sequential_2/dense_9/Tensordot/transpose:y:0-sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_9/Tensordot/MatMulMatMul/sequential_2/dense_9/Tensordot/Reshape:output:05sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/concat_1ConcatV20sequential_2/dense_9/Tensordot/GatherV2:output:0/sequential_2/dense_9/Tensordot/Const_2:output:05sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_9/TensordotReshape/sequential_2/dense_9/Tensordot/MatMul:product:00sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_9/BiasAddBiasAdd'sequential_2/dense_9/Tensordot:output:03sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d]
dropout_10/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_10/dropout/MulMul%sequential_2/dense_9/BiasAdd:output:0!dropout_10/dropout/Const:output:0*
T0*+
_output_shapes
:���������dm
dropout_10/dropout/ShapeShape%sequential_2/dense_9/BiasAdd:output:0*
T0*
_output_shapes
:�
/dropout_10/dropout/random_uniform/RandomUniformRandomUniform!dropout_10/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0f
!dropout_10/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_10/dropout/GreaterEqualGreaterEqual8dropout_10/dropout/random_uniform/RandomUniform:output:0*dropout_10/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
dropout_10/dropout/CastCast#dropout_10/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
dropout_10/dropout/Mul_1Muldropout_10/dropout/Mul:z:0dropout_10/dropout/Cast:y:0*
T0*+
_output_shapes
:���������d�
add_1AddV2)layer_normalization_4/batchnorm/add_1:z:0dropout_10/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_5/moments/meanMean	add_1:z:0=layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_5/moments/StopGradientStopGradient+layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_5/moments/SquaredDifferenceSquaredDifference	add_1:z:03layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_5/moments/varianceMean3layer_normalization_5/moments/SquaredDifference:z:0Alayer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_5/batchnorm/addAddV2/layer_normalization_5/moments/variance:output:0.layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/RsqrtRsqrt'layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/mulMul)layer_normalization_5/batchnorm/Rsqrt:y:0:layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_1Mul	add_1:z:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_2Mul+layer_normalization_5/moments/mean:output:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_5/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/subSub6layer_normalization_5/batchnorm/ReadVariableOp:value:0)layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/add_1AddV2)layer_normalization_5/batchnorm/mul_1:z:0'layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d|
IdentityIdentity)layer_normalization_5/batchnorm/add_1:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp/^layer_normalization_4/batchnorm/ReadVariableOp3^layer_normalization_4/batchnorm/mul/ReadVariableOp/^layer_normalization_5/batchnorm/ReadVariableOp3^layer_normalization_5/batchnorm/mul/ReadVariableOp;^multi_head_attention_2/attention_output/add/ReadVariableOpE^multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp.^multi_head_attention_2/key/add/ReadVariableOp8^multi_head_attention_2/key/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/query/add/ReadVariableOp:^multi_head_attention_2/query/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/value/add/ReadVariableOp:^multi_head_attention_2/value/einsum/Einsum/ReadVariableOp,^sequential_2/dense_8/BiasAdd/ReadVariableOp.^sequential_2/dense_8/Tensordot/ReadVariableOp,^sequential_2/dense_9/BiasAdd/ReadVariableOp.^sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 2`
.layer_normalization_4/batchnorm/ReadVariableOp.layer_normalization_4/batchnorm/ReadVariableOp2h
2layer_normalization_4/batchnorm/mul/ReadVariableOp2layer_normalization_4/batchnorm/mul/ReadVariableOp2`
.layer_normalization_5/batchnorm/ReadVariableOp.layer_normalization_5/batchnorm/ReadVariableOp2h
2layer_normalization_5/batchnorm/mul/ReadVariableOp2layer_normalization_5/batchnorm/mul/ReadVariableOp2x
:multi_head_attention_2/attention_output/add/ReadVariableOp:multi_head_attention_2/attention_output/add/ReadVariableOp2�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpDmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2^
-multi_head_attention_2/key/add/ReadVariableOp-multi_head_attention_2/key/add/ReadVariableOp2r
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/query/add/ReadVariableOp/multi_head_attention_2/query/add/ReadVariableOp2v
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/value/add/ReadVariableOp/multi_head_attention_2/value/add/ReadVariableOp2v
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2Z
+sequential_2/dense_8/BiasAdd/ReadVariableOp+sequential_2/dense_8/BiasAdd/ReadVariableOp2^
-sequential_2/dense_8/Tensordot/ReadVariableOp-sequential_2/dense_8/Tensordot/ReadVariableOp2Z
+sequential_2/dense_9/BiasAdd/ReadVariableOp+sequential_2/dense_9/BiasAdd/ReadVariableOp2^
-sequential_2/dense_9/Tensordot/ReadVariableOp-sequential_2/dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�*
�	
B__inference_model_2_layer_call_and_return_conditional_losses_52932

inputs6
$token_and_position_embedding_2_52716:d7
$token_and_position_embedding_2_52718:	�/
transformer_block_2_52849:+
transformer_block_2_52851:/
transformer_block_2_52853:+
transformer_block_2_52855:/
transformer_block_2_52857:+
transformer_block_2_52859:/
transformer_block_2_52861:'
transformer_block_2_52863:'
transformer_block_2_52865:'
transformer_block_2_52867:+
transformer_block_2_52869:'
transformer_block_2_52871:+
transformer_block_2_52873:'
transformer_block_2_52875:'
transformer_block_2_52877:'
transformer_block_2_52879: 
dense_10_52902:
dense_10_52904: 
dense_11_52926:
dense_11_52928:
identity�� dense_10/StatefulPartitionedCall� dense_11/StatefulPartitionedCall�6token_and_position_embedding_2/StatefulPartitionedCall�+transformer_block_2/StatefulPartitionedCall�
6token_and_position_embedding_2/StatefulPartitionedCallStatefulPartitionedCallinputs$token_and_position_embedding_2_52716$token_and_position_embedding_2_52718*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *b
f]R[
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715�
+transformer_block_2/StatefulPartitionedCallStatefulPartitionedCall?token_and_position_embedding_2/StatefulPartitionedCall:output:0transformer_block_2_52849transformer_block_2_52851transformer_block_2_52853transformer_block_2_52855transformer_block_2_52857transformer_block_2_52859transformer_block_2_52861transformer_block_2_52863transformer_block_2_52865transformer_block_2_52867transformer_block_2_52869transformer_block_2_52871transformer_block_2_52873transformer_block_2_52875transformer_block_2_52877transformer_block_2_52879*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_52848�
*global_average_pooling1d_2/PartitionedCallPartitionedCall4transformer_block_2/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *^
fYRW
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681�
dropout_11/PartitionedCallPartitionedCall3global_average_pooling1d_2/PartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_52888�
 dense_10/StatefulPartitionedCallStatefulPartitionedCall#dropout_11/PartitionedCall:output:0dense_10_52902dense_10_52904*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_10_layer_call_and_return_conditional_losses_52901�
dropout_12/PartitionedCallPartitionedCall)dense_10/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_52912�
 dense_11/StatefulPartitionedCallStatefulPartitionedCall#dropout_12/PartitionedCall:output:0dense_11_52926dense_11_52928*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_11_layer_call_and_return_conditional_losses_52925x
IdentityIdentity)dense_11/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp!^dense_10/StatefulPartitionedCall!^dense_11/StatefulPartitionedCall7^token_and_position_embedding_2/StatefulPartitionedCall,^transformer_block_2/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2D
 dense_10/StatefulPartitionedCall dense_10/StatefulPartitionedCall2D
 dense_11/StatefulPartitionedCall dense_11/StatefulPartitionedCall2p
6token_and_position_embedding_2/StatefulPartitionedCall6token_and_position_embedding_2/StatefulPartitionedCall2Z
+transformer_block_2/StatefulPartitionedCall+transformer_block_2/StatefulPartitionedCall:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�>
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_54713

inputs;
)dense_8_tensordot_readvariableop_resource:5
'dense_8_biasadd_readvariableop_resource:;
)dense_9_tensordot_readvariableop_resource:5
'dense_9_biasadd_readvariableop_resource:
identity��dense_8/BiasAdd/ReadVariableOp� dense_8/Tensordot/ReadVariableOp�dense_9/BiasAdd/ReadVariableOp� dense_9/Tensordot/ReadVariableOp�
 dense_8/Tensordot/ReadVariableOpReadVariableOp)dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0`
dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:g
dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       M
dense_8/Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:a
dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/GatherV2GatherV2 dense_8/Tensordot/Shape:output:0dense_8/Tensordot/free:output:0(dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:c
!dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/GatherV2_1GatherV2 dense_8/Tensordot/Shape:output:0dense_8/Tensordot/axes:output:0*dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:a
dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
dense_8/Tensordot/ProdProd#dense_8/Tensordot/GatherV2:output:0 dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: c
dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
dense_8/Tensordot/Prod_1Prod%dense_8/Tensordot/GatherV2_1:output:0"dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: _
dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/concatConcatV2dense_8/Tensordot/free:output:0dense_8/Tensordot/axes:output:0&dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
dense_8/Tensordot/stackPackdense_8/Tensordot/Prod:output:0!dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
dense_8/Tensordot/transpose	Transposeinputs!dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
dense_8/Tensordot/ReshapeReshapedense_8/Tensordot/transpose:y:0 dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
dense_8/Tensordot/MatMulMatMul"dense_8/Tensordot/Reshape:output:0(dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������c
dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:a
dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/concat_1ConcatV2#dense_8/Tensordot/GatherV2:output:0"dense_8/Tensordot/Const_2:output:0(dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
dense_8/TensordotReshape"dense_8/Tensordot/MatMul:product:0#dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
dense_8/BiasAdd/ReadVariableOpReadVariableOp'dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_8/BiasAddBiasAdddense_8/Tensordot:output:0&dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dd
dense_8/ReluReludense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
 dense_9/Tensordot/ReadVariableOpReadVariableOp)dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0`
dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:g
dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       a
dense_9/Tensordot/ShapeShapedense_8/Relu:activations:0*
T0*
_output_shapes
:a
dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/GatherV2GatherV2 dense_9/Tensordot/Shape:output:0dense_9/Tensordot/free:output:0(dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:c
!dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/GatherV2_1GatherV2 dense_9/Tensordot/Shape:output:0dense_9/Tensordot/axes:output:0*dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:a
dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
dense_9/Tensordot/ProdProd#dense_9/Tensordot/GatherV2:output:0 dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: c
dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
dense_9/Tensordot/Prod_1Prod%dense_9/Tensordot/GatherV2_1:output:0"dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: _
dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/concatConcatV2dense_9/Tensordot/free:output:0dense_9/Tensordot/axes:output:0&dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
dense_9/Tensordot/stackPackdense_9/Tensordot/Prod:output:0!dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
dense_9/Tensordot/transpose	Transposedense_8/Relu:activations:0!dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
dense_9/Tensordot/ReshapeReshapedense_9/Tensordot/transpose:y:0 dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
dense_9/Tensordot/MatMulMatMul"dense_9/Tensordot/Reshape:output:0(dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������c
dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:a
dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/concat_1ConcatV2#dense_9/Tensordot/GatherV2:output:0"dense_9/Tensordot/Const_2:output:0(dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
dense_9/TensordotReshape"dense_9/Tensordot/MatMul:product:0#dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
dense_9/BiasAdd/ReadVariableOpReadVariableOp'dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_9/BiasAddBiasAdddense_9/Tensordot:output:0&dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dk
IdentityIdentitydense_9/BiasAdd:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp^dense_8/BiasAdd/ReadVariableOp!^dense_8/Tensordot/ReadVariableOp^dense_9/BiasAdd/ReadVariableOp!^dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2@
dense_8/BiasAdd/ReadVariableOpdense_8/BiasAdd/ReadVariableOp2D
 dense_8/Tensordot/ReadVariableOp dense_8/Tensordot/ReadVariableOp2@
dense_9/BiasAdd/ReadVariableOpdense_9/BiasAdd/ReadVariableOp2D
 dense_9/Tensordot/ReadVariableOp dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
��
�
B__inference_model_2_layer_call_and_return_conditional_losses_54094

inputsS
Atoken_and_position_embedding_2_embedding_5_embedding_lookup_53913:dT
Atoken_and_position_embedding_2_embedding_4_embedding_lookup_53919:	�l
Vtransformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource:^
Ltransformer_block_2_multi_head_attention_2_query_add_readvariableop_resource:j
Ttransformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource:\
Jtransformer_block_2_multi_head_attention_2_key_add_readvariableop_resource:l
Vtransformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource:^
Ltransformer_block_2_multi_head_attention_2_value_add_readvariableop_resource:w
atransformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:e
Wtransformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource:]
Otransformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource:Y
Ktransformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource:\
Jtransformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource:V
Htransformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource:\
Jtransformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource:V
Htransformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource:]
Otransformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource:Y
Ktransformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource:9
'dense_10_matmul_readvariableop_resource:6
(dense_10_biasadd_readvariableop_resource:9
'dense_11_matmul_readvariableop_resource:6
(dense_11_biasadd_readvariableop_resource:
identity��dense_10/BiasAdd/ReadVariableOp�dense_10/MatMul/ReadVariableOp�dense_11/BiasAdd/ReadVariableOp�dense_11/MatMul/ReadVariableOp�;token_and_position_embedding_2/embedding_4/embedding_lookup�;token_and_position_embedding_2/embedding_5/embedding_lookup�Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp�Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp�Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp�Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp�Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp�Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp�Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp�Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp�Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp�Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp�?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp�Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpZ
$token_and_position_embedding_2/ShapeShapeinputs*
T0*
_output_shapes
:�
2token_and_position_embedding_2/strided_slice/stackConst*
_output_shapes
:*
dtype0*
valueB:
���������~
4token_and_position_embedding_2/strided_slice/stack_1Const*
_output_shapes
:*
dtype0*
valueB: ~
4token_and_position_embedding_2/strided_slice/stack_2Const*
_output_shapes
:*
dtype0*
valueB:�
,token_and_position_embedding_2/strided_sliceStridedSlice-token_and_position_embedding_2/Shape:output:0;token_and_position_embedding_2/strided_slice/stack:output:0=token_and_position_embedding_2/strided_slice/stack_1:output:0=token_and_position_embedding_2/strided_slice/stack_2:output:0*
Index0*
T0*
_output_shapes
: *
shrink_axis_maskl
*token_and_position_embedding_2/range/startConst*
_output_shapes
: *
dtype0*
value	B : l
*token_and_position_embedding_2/range/deltaConst*
_output_shapes
: *
dtype0*
value	B :�
$token_and_position_embedding_2/rangeRange3token_and_position_embedding_2/range/start:output:05token_and_position_embedding_2/strided_slice:output:03token_and_position_embedding_2/range/delta:output:0*
_output_shapes
:d�
;token_and_position_embedding_2/embedding_5/embedding_lookupResourceGatherAtoken_and_position_embedding_2_embedding_5_embedding_lookup_53913-token_and_position_embedding_2/range:output:0*
Tindices0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_5/embedding_lookup/53913*
_output_shapes

:d*
dtype0�
Dtoken_and_position_embedding_2/embedding_5/embedding_lookup/IdentityIdentityDtoken_and_position_embedding_2/embedding_5/embedding_lookup:output:0*
T0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_5/embedding_lookup/53913*
_output_shapes

:d�
Ftoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1IdentityMtoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity:output:0*
T0*
_output_shapes

:d�
/token_and_position_embedding_2/embedding_4/CastCastinputs*

DstT0*

SrcT0*'
_output_shapes
:���������d�
;token_and_position_embedding_2/embedding_4/embedding_lookupResourceGatherAtoken_and_position_embedding_2_embedding_4_embedding_lookup_539193token_and_position_embedding_2/embedding_4/Cast:y:0*
Tindices0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_4/embedding_lookup/53919*+
_output_shapes
:���������d*
dtype0�
Dtoken_and_position_embedding_2/embedding_4/embedding_lookup/IdentityIdentityDtoken_and_position_embedding_2/embedding_4/embedding_lookup:output:0*
T0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_4/embedding_lookup/53919*+
_output_shapes
:���������d�
Ftoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1IdentityMtoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity:output:0*
T0*+
_output_shapes
:���������d�
"token_and_position_embedding_2/addAddV2Otoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1:output:0Otoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1:output:0*
T0*+
_output_shapes
:���������d�
Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpVtransformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
>transformer_block_2/multi_head_attention_2/query/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Utransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOpReadVariableOpLtransformer_block_2_multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
4transformer_block_2/multi_head_attention_2/query/addAddV2Gtransformer_block_2/multi_head_attention_2/query/einsum/Einsum:output:0Ktransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOpTtransformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
<transformer_block_2/multi_head_attention_2/key/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Stransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOpReadVariableOpJtransformer_block_2_multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
2transformer_block_2/multi_head_attention_2/key/addAddV2Etransformer_block_2/multi_head_attention_2/key/einsum/Einsum:output:0Itransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpVtransformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
>transformer_block_2/multi_head_attention_2/value/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Utransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOpReadVariableOpLtransformer_block_2_multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
4transformer_block_2/multi_head_attention_2/value/addAddV2Gtransformer_block_2/multi_head_attention_2/value/einsum/Einsum:output:0Ktransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������du
0transformer_block_2/multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
.transformer_block_2/multi_head_attention_2/MulMul8transformer_block_2/multi_head_attention_2/query/add:z:09transformer_block_2/multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
8transformer_block_2/multi_head_attention_2/einsum/EinsumEinsum6transformer_block_2/multi_head_attention_2/key/add:z:02transformer_block_2/multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
:transformer_block_2/multi_head_attention_2/softmax/SoftmaxSoftmaxAtransformer_block_2/multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
:transformer_block_2/multi_head_attention_2/einsum_1/EinsumEinsumDtransformer_block_2/multi_head_attention_2/softmax/Softmax:softmax:08transformer_block_2/multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpatransformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Itransformer_block_2/multi_head_attention_2/attention_output/einsum/EinsumEinsumCtransformer_block_2/multi_head_attention_2/einsum_1/Einsum:output:0`transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpWtransformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
?transformer_block_2/multi_head_attention_2/attention_output/addAddV2Rtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum:output:0Vtransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dp
+transformer_block_2/dropout_9/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
)transformer_block_2/dropout_9/dropout/MulMulCtransformer_block_2/multi_head_attention_2/attention_output/add:z:04transformer_block_2/dropout_9/dropout/Const:output:0*
T0*+
_output_shapes
:���������d�
+transformer_block_2/dropout_9/dropout/ShapeShapeCtransformer_block_2/multi_head_attention_2/attention_output/add:z:0*
T0*
_output_shapes
:�
Btransformer_block_2/dropout_9/dropout/random_uniform/RandomUniformRandomUniform4transformer_block_2/dropout_9/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0y
4transformer_block_2/dropout_9/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
2transformer_block_2/dropout_9/dropout/GreaterEqualGreaterEqualKtransformer_block_2/dropout_9/dropout/random_uniform/RandomUniform:output:0=transformer_block_2/dropout_9/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
*transformer_block_2/dropout_9/dropout/CastCast6transformer_block_2/dropout_9/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
+transformer_block_2/dropout_9/dropout/Mul_1Mul-transformer_block_2/dropout_9/dropout/Mul:z:0.transformer_block_2/dropout_9/dropout/Cast:y:0*
T0*+
_output_shapes
:���������d�
transformer_block_2/addAddV2&token_and_position_embedding_2/add:z:0/transformer_block_2/dropout_9/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d�
Htransformer_block_2/layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
6transformer_block_2/layer_normalization_4/moments/meanMeantransformer_block_2/add:z:0Qtransformer_block_2/layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
>transformer_block_2/layer_normalization_4/moments/StopGradientStopGradient?transformer_block_2/layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Ctransformer_block_2/layer_normalization_4/moments/SquaredDifferenceSquaredDifferencetransformer_block_2/add:z:0Gtransformer_block_2/layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Ltransformer_block_2/layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
:transformer_block_2/layer_normalization_4/moments/varianceMeanGtransformer_block_2/layer_normalization_4/moments/SquaredDifference:z:0Utransformer_block_2/layer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(~
9transformer_block_2/layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
7transformer_block_2/layer_normalization_4/batchnorm/addAddV2Ctransformer_block_2/layer_normalization_4/moments/variance:output:0Btransformer_block_2/layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/RsqrtRsqrt;transformer_block_2/layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOpOtransformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_4/batchnorm/mulMul=transformer_block_2/layer_normalization_4/batchnorm/Rsqrt:y:0Ntransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/mul_1Multransformer_block_2/add:z:0;transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/mul_2Mul?transformer_block_2/layer_normalization_4/moments/mean:output:0;transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpReadVariableOpKtransformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_4/batchnorm/subSubJtransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp:value:0=transformer_block_2/layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/add_1AddV2=transformer_block_2/layer_normalization_4/batchnorm/mul_1:z:0;transformer_block_2/layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOpJtransformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
7transformer_block_2/sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
7transformer_block_2/sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
8transformer_block_2/sequential_2/dense_8/Tensordot/ShapeShape=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:�
@transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2GatherV2Atransformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Btransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
=transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1GatherV2Atransformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Ktransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
7transformer_block_2/sequential_2/dense_8/Tensordot/ProdProdDtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Atransformer_block_2/sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: �
:transformer_block_2/sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
9transformer_block_2/sequential_2/dense_8/Tensordot/Prod_1ProdFtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1:output:0Ctransformer_block_2/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
>transformer_block_2/sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
9transformer_block_2/sequential_2/dense_8/Tensordot/concatConcatV2@transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Gtransformer_block_2/sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_8/Tensordot/stackPack@transformer_block_2/sequential_2/dense_8/Tensordot/Prod:output:0Btransformer_block_2/sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
<transformer_block_2/sequential_2/dense_8/Tensordot/transpose	Transpose=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0Btransformer_block_2/sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
:transformer_block_2/sequential_2/dense_8/Tensordot/ReshapeReshape@transformer_block_2/sequential_2/dense_8/Tensordot/transpose:y:0Atransformer_block_2/sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
9transformer_block_2/sequential_2/dense_8/Tensordot/MatMulMatMulCtransformer_block_2/sequential_2/dense_8/Tensordot/Reshape:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
:transformer_block_2/sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
@transformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_8/Tensordot/concat_1ConcatV2Dtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Ctransformer_block_2/sequential_2/dense_8/Tensordot/Const_2:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
2transformer_block_2/sequential_2/dense_8/TensordotReshapeCtransformer_block_2/sequential_2/dense_8/Tensordot/MatMul:product:0Dtransformer_block_2/sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOpHtransformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
0transformer_block_2/sequential_2/dense_8/BiasAddBiasAdd;transformer_block_2/sequential_2/dense_8/Tensordot:output:0Gtransformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
-transformer_block_2/sequential_2/dense_8/ReluRelu9transformer_block_2/sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOpJtransformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
7transformer_block_2/sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
7transformer_block_2/sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
8transformer_block_2/sequential_2/dense_9/Tensordot/ShapeShape;transformer_block_2/sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:�
@transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2GatherV2Atransformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Btransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
=transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1GatherV2Atransformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Ktransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
7transformer_block_2/sequential_2/dense_9/Tensordot/ProdProdDtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Atransformer_block_2/sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: �
:transformer_block_2/sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
9transformer_block_2/sequential_2/dense_9/Tensordot/Prod_1ProdFtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1:output:0Ctransformer_block_2/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
>transformer_block_2/sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
9transformer_block_2/sequential_2/dense_9/Tensordot/concatConcatV2@transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Gtransformer_block_2/sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_9/Tensordot/stackPack@transformer_block_2/sequential_2/dense_9/Tensordot/Prod:output:0Btransformer_block_2/sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
<transformer_block_2/sequential_2/dense_9/Tensordot/transpose	Transpose;transformer_block_2/sequential_2/dense_8/Relu:activations:0Btransformer_block_2/sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
:transformer_block_2/sequential_2/dense_9/Tensordot/ReshapeReshape@transformer_block_2/sequential_2/dense_9/Tensordot/transpose:y:0Atransformer_block_2/sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
9transformer_block_2/sequential_2/dense_9/Tensordot/MatMulMatMulCtransformer_block_2/sequential_2/dense_9/Tensordot/Reshape:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
:transformer_block_2/sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
@transformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_9/Tensordot/concat_1ConcatV2Dtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Ctransformer_block_2/sequential_2/dense_9/Tensordot/Const_2:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
2transformer_block_2/sequential_2/dense_9/TensordotReshapeCtransformer_block_2/sequential_2/dense_9/Tensordot/MatMul:product:0Dtransformer_block_2/sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOpHtransformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
0transformer_block_2/sequential_2/dense_9/BiasAddBiasAdd;transformer_block_2/sequential_2/dense_9/Tensordot:output:0Gtransformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dq
,transformer_block_2/dropout_10/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
*transformer_block_2/dropout_10/dropout/MulMul9transformer_block_2/sequential_2/dense_9/BiasAdd:output:05transformer_block_2/dropout_10/dropout/Const:output:0*
T0*+
_output_shapes
:���������d�
,transformer_block_2/dropout_10/dropout/ShapeShape9transformer_block_2/sequential_2/dense_9/BiasAdd:output:0*
T0*
_output_shapes
:�
Ctransformer_block_2/dropout_10/dropout/random_uniform/RandomUniformRandomUniform5transformer_block_2/dropout_10/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0z
5transformer_block_2/dropout_10/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
3transformer_block_2/dropout_10/dropout/GreaterEqualGreaterEqualLtransformer_block_2/dropout_10/dropout/random_uniform/RandomUniform:output:0>transformer_block_2/dropout_10/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
+transformer_block_2/dropout_10/dropout/CastCast7transformer_block_2/dropout_10/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
,transformer_block_2/dropout_10/dropout/Mul_1Mul.transformer_block_2/dropout_10/dropout/Mul:z:0/transformer_block_2/dropout_10/dropout/Cast:y:0*
T0*+
_output_shapes
:���������d�
transformer_block_2/add_1AddV2=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:00transformer_block_2/dropout_10/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d�
Htransformer_block_2/layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
6transformer_block_2/layer_normalization_5/moments/meanMeantransformer_block_2/add_1:z:0Qtransformer_block_2/layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
>transformer_block_2/layer_normalization_5/moments/StopGradientStopGradient?transformer_block_2/layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Ctransformer_block_2/layer_normalization_5/moments/SquaredDifferenceSquaredDifferencetransformer_block_2/add_1:z:0Gtransformer_block_2/layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Ltransformer_block_2/layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
:transformer_block_2/layer_normalization_5/moments/varianceMeanGtransformer_block_2/layer_normalization_5/moments/SquaredDifference:z:0Utransformer_block_2/layer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(~
9transformer_block_2/layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
7transformer_block_2/layer_normalization_5/batchnorm/addAddV2Ctransformer_block_2/layer_normalization_5/moments/variance:output:0Btransformer_block_2/layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/RsqrtRsqrt;transformer_block_2/layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOpOtransformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_5/batchnorm/mulMul=transformer_block_2/layer_normalization_5/batchnorm/Rsqrt:y:0Ntransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/mul_1Multransformer_block_2/add_1:z:0;transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/mul_2Mul?transformer_block_2/layer_normalization_5/moments/mean:output:0;transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpReadVariableOpKtransformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_5/batchnorm/subSubJtransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp:value:0=transformer_block_2/layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/add_1AddV2=transformer_block_2/layer_normalization_5/batchnorm/mul_1:z:0;transformer_block_2/layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������ds
1global_average_pooling1d_2/Mean/reduction_indicesConst*
_output_shapes
: *
dtype0*
value	B :�
global_average_pooling1d_2/MeanMean=transformer_block_2/layer_normalization_5/batchnorm/add_1:z:0:global_average_pooling1d_2/Mean/reduction_indices:output:0*
T0*'
_output_shapes
:���������]
dropout_11/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_11/dropout/MulMul(global_average_pooling1d_2/Mean:output:0!dropout_11/dropout/Const:output:0*
T0*'
_output_shapes
:���������p
dropout_11/dropout/ShapeShape(global_average_pooling1d_2/Mean:output:0*
T0*
_output_shapes
:�
/dropout_11/dropout/random_uniform/RandomUniformRandomUniform!dropout_11/dropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0f
!dropout_11/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_11/dropout/GreaterEqualGreaterEqual8dropout_11/dropout/random_uniform/RandomUniform:output:0*dropout_11/dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:����������
dropout_11/dropout/CastCast#dropout_11/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:����������
dropout_11/dropout/Mul_1Muldropout_11/dropout/Mul:z:0dropout_11/dropout/Cast:y:0*
T0*'
_output_shapes
:����������
dense_10/MatMul/ReadVariableOpReadVariableOp'dense_10_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
dense_10/MatMulMatMuldropout_11/dropout/Mul_1:z:0&dense_10/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
dense_10/BiasAdd/ReadVariableOpReadVariableOp(dense_10_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_10/BiasAddBiasAdddense_10/MatMul:product:0'dense_10/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������b
dense_10/ReluReludense_10/BiasAdd:output:0*
T0*'
_output_shapes
:���������]
dropout_12/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_12/dropout/MulMuldense_10/Relu:activations:0!dropout_12/dropout/Const:output:0*
T0*'
_output_shapes
:���������c
dropout_12/dropout/ShapeShapedense_10/Relu:activations:0*
T0*
_output_shapes
:�
/dropout_12/dropout/random_uniform/RandomUniformRandomUniform!dropout_12/dropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0f
!dropout_12/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_12/dropout/GreaterEqualGreaterEqual8dropout_12/dropout/random_uniform/RandomUniform:output:0*dropout_12/dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:����������
dropout_12/dropout/CastCast#dropout_12/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:����������
dropout_12/dropout/Mul_1Muldropout_12/dropout/Mul:z:0dropout_12/dropout/Cast:y:0*
T0*'
_output_shapes
:����������
dense_11/MatMul/ReadVariableOpReadVariableOp'dense_11_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
dense_11/MatMulMatMuldropout_12/dropout/Mul_1:z:0&dense_11/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
dense_11/BiasAdd/ReadVariableOpReadVariableOp(dense_11_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_11/BiasAddBiasAdddense_11/MatMul:product:0'dense_11/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������h
dense_11/SoftmaxSoftmaxdense_11/BiasAdd:output:0*
T0*'
_output_shapes
:���������i
IdentityIdentitydense_11/Softmax:softmax:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp ^dense_10/BiasAdd/ReadVariableOp^dense_10/MatMul/ReadVariableOp ^dense_11/BiasAdd/ReadVariableOp^dense_11/MatMul/ReadVariableOp<^token_and_position_embedding_2/embedding_4/embedding_lookup<^token_and_position_embedding_2/embedding_5/embedding_lookupC^transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpG^transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpC^transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpG^transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpO^transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpY^transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpB^transformer_block_2/multi_head_attention_2/key/add/ReadVariableOpL^transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpD^transformer_block_2/multi_head_attention_2/query/add/ReadVariableOpN^transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpD^transformer_block_2/multi_head_attention_2/value/add/ReadVariableOpN^transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp@^transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpB^transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp@^transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpB^transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2B
dense_10/BiasAdd/ReadVariableOpdense_10/BiasAdd/ReadVariableOp2@
dense_10/MatMul/ReadVariableOpdense_10/MatMul/ReadVariableOp2B
dense_11/BiasAdd/ReadVariableOpdense_11/BiasAdd/ReadVariableOp2@
dense_11/MatMul/ReadVariableOpdense_11/MatMul/ReadVariableOp2z
;token_and_position_embedding_2/embedding_4/embedding_lookup;token_and_position_embedding_2/embedding_4/embedding_lookup2z
;token_and_position_embedding_2/embedding_5/embedding_lookup;token_and_position_embedding_2/embedding_5/embedding_lookup2�
Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpBtransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp2�
Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpFtransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp2�
Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpBtransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp2�
Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpFtransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp2�
Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpNtransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp2�
Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpXtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2�
Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOpAtransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp2�
Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpKtransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2�
Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOpCtransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp2�
Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpMtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2�
Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOpCtransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp2�
Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpMtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2�
?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp2�
Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpAtransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp2�
?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp2�
Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpAtransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52559

inputs
dense_8_52517:
dense_8_52519:
dense_9_52553:
dense_9_52555:
identity��dense_8/StatefulPartitionedCall�dense_9/StatefulPartitionedCall�
dense_8/StatefulPartitionedCallStatefulPartitionedCallinputsdense_8_52517dense_8_52519*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_8_layer_call_and_return_conditional_losses_52516�
dense_9/StatefulPartitionedCallStatefulPartitionedCall(dense_8/StatefulPartitionedCall:output:0dense_9_52553dense_9_52555*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_9_layer_call_and_return_conditional_losses_52552{
IdentityIdentity(dense_9/StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp ^dense_8/StatefulPartitionedCall ^dense_9/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2B
dense_8/StatefulPartitionedCalldense_8/StatefulPartitionedCall2B
dense_9/StatefulPartitionedCalldense_9/StatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
,__inference_sequential_2_layer_call_fn_52570
dense_8_input
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCalldense_8_inputunknown	unknown_0	unknown_1	unknown_2*
Tin	
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*&
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *P
fKRI
G__inference_sequential_2_layer_call_and_return_conditional_losses_52559s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 22
StatefulPartitionedCallStatefulPartitionedCall:Z V
+
_output_shapes
:���������d
'
_user_specified_namedense_8_input
�
V
:__inference_global_average_pooling1d_2_layer_call_fn_54473

inputs
identity�
PartitionedCallPartitionedCallinputs*
Tin
2*
Tout
2*
_collective_manager_ids
 *0
_output_shapes
:������������������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *^
fYRW
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681i
IdentityIdentityPartitionedCall:output:0*
T0*0
_output_shapes
:������������������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*<
_input_shapes+
):'���������������������������:e a
=
_output_shapes+
):'���������������������������
 
_user_specified_nameinputs
�
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52619

inputs
dense_8_52608:
dense_8_52610:
dense_9_52613:
dense_9_52615:
identity��dense_8/StatefulPartitionedCall�dense_9/StatefulPartitionedCall�
dense_8/StatefulPartitionedCallStatefulPartitionedCallinputsdense_8_52608dense_8_52610*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_8_layer_call_and_return_conditional_losses_52516�
dense_9/StatefulPartitionedCallStatefulPartitionedCall(dense_8/StatefulPartitionedCall:output:0dense_9_52613dense_9_52615*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_9_layer_call_and_return_conditional_losses_52552{
IdentityIdentity(dense_9/StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp ^dense_8/StatefulPartitionedCall ^dense_9/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2B
dense_8/StatefulPartitionedCalldense_8/StatefulPartitionedCall2B
dense_9/StatefulPartitionedCalldense_9/StatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�	
d
E__inference_dropout_11_layer_call_and_return_conditional_losses_54506

inputs
identity�R
dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?d
dropout/MulMulinputsdropout/Const:output:0*
T0*'
_output_shapes
:���������C
dropout/ShapeShapeinputs*
T0*
_output_shapes
:�
$dropout/random_uniform/RandomUniformRandomUniformdropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0[
dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout/GreaterEqualGreaterEqual-dropout/random_uniform/RandomUniform:output:0dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:���������o
dropout/CastCastdropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:���������i
dropout/Mul_1Muldropout/Mul:z:0dropout/Cast:y:0*
T0*'
_output_shapes
:���������Y
IdentityIdentitydropout/Mul_1:z:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�	
d
E__inference_dropout_12_layer_call_and_return_conditional_losses_53009

inputs
identity�R
dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?d
dropout/MulMulinputsdropout/Const:output:0*
T0*'
_output_shapes
:���������C
dropout/ShapeShapeinputs*
T0*
_output_shapes
:�
$dropout/random_uniform/RandomUniformRandomUniformdropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0[
dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout/GreaterEqualGreaterEqual-dropout/random_uniform/RandomUniform:output:0dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:���������o
dropout/CastCastdropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:���������i
dropout/Mul_1Muldropout/Mul:z:0dropout/Cast:y:0*
T0*'
_output_shapes
:���������Y
IdentityIdentitydropout/Mul_1:z:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52671
dense_8_input
dense_8_52660:
dense_8_52662:
dense_9_52665:
dense_9_52667:
identity��dense_8/StatefulPartitionedCall�dense_9/StatefulPartitionedCall�
dense_8/StatefulPartitionedCallStatefulPartitionedCalldense_8_inputdense_8_52660dense_8_52662*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_8_layer_call_and_return_conditional_losses_52516�
dense_9/StatefulPartitionedCallStatefulPartitionedCall(dense_8/StatefulPartitionedCall:output:0dense_9_52665dense_9_52667*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_9_layer_call_and_return_conditional_losses_52552{
IdentityIdentity(dense_9/StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp ^dense_8/StatefulPartitionedCall ^dense_9/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2B
dense_8/StatefulPartitionedCalldense_8/StatefulPartitionedCall2B
dense_9/StatefulPartitionedCalldense_9/StatefulPartitionedCall:Z V
+
_output_shapes
:���������d
'
_user_specified_namedense_8_input
��
�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54468

inputsX
Bmulti_head_attention_2_query_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_query_add_readvariableop_resource:V
@multi_head_attention_2_key_einsum_einsum_readvariableop_resource:H
6multi_head_attention_2_key_add_readvariableop_resource:X
Bmulti_head_attention_2_value_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_value_add_readvariableop_resource:c
Mmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:Q
Cmulti_head_attention_2_attention_output_add_readvariableop_resource:I
;layer_normalization_4_batchnorm_mul_readvariableop_resource:E
7layer_normalization_4_batchnorm_readvariableop_resource:H
6sequential_2_dense_8_tensordot_readvariableop_resource:B
4sequential_2_dense_8_biasadd_readvariableop_resource:H
6sequential_2_dense_9_tensordot_readvariableop_resource:B
4sequential_2_dense_9_biasadd_readvariableop_resource:I
;layer_normalization_5_batchnorm_mul_readvariableop_resource:E
7layer_normalization_5_batchnorm_readvariableop_resource:
identity��.layer_normalization_4/batchnorm/ReadVariableOp�2layer_normalization_4/batchnorm/mul/ReadVariableOp�.layer_normalization_5/batchnorm/ReadVariableOp�2layer_normalization_5/batchnorm/mul/ReadVariableOp�:multi_head_attention_2/attention_output/add/ReadVariableOp�Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�-multi_head_attention_2/key/add/ReadVariableOp�7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/query/add/ReadVariableOp�9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/value/add/ReadVariableOp�9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�+sequential_2/dense_8/BiasAdd/ReadVariableOp�-sequential_2/dense_8/Tensordot/ReadVariableOp�+sequential_2/dense_9/BiasAdd/ReadVariableOp�-sequential_2/dense_9/Tensordot/ReadVariableOp�
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/query/einsum/EinsumEinsuminputsAmulti_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/query/add/ReadVariableOpReadVariableOp8multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/query/addAddV23multi_head_attention_2/query/einsum/Einsum:output:07multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOp@multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
(multi_head_attention_2/key/einsum/EinsumEinsuminputs?multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
-multi_head_attention_2/key/add/ReadVariableOpReadVariableOp6multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
multi_head_attention_2/key/addAddV21multi_head_attention_2/key/einsum/Einsum:output:05multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/value/einsum/EinsumEinsuminputsAmulti_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/value/add/ReadVariableOpReadVariableOp8multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/value/addAddV23multi_head_attention_2/value/einsum/Einsum:output:07multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������da
multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
multi_head_attention_2/MulMul$multi_head_attention_2/query/add:z:0%multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
$multi_head_attention_2/einsum/EinsumEinsum"multi_head_attention_2/key/add:z:0multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
&multi_head_attention_2/softmax/SoftmaxSoftmax-multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
&multi_head_attention_2/einsum_1/EinsumEinsum0multi_head_attention_2/softmax/Softmax:softmax:0$multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpMmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
5multi_head_attention_2/attention_output/einsum/EinsumEinsum/multi_head_attention_2/einsum_1/Einsum:output:0Lmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
:multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpCmulti_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
+multi_head_attention_2/attention_output/addAddV2>multi_head_attention_2/attention_output/einsum/Einsum:output:0Bmulti_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d\
dropout_9/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_9/dropout/MulMul/multi_head_attention_2/attention_output/add:z:0 dropout_9/dropout/Const:output:0*
T0*+
_output_shapes
:���������dv
dropout_9/dropout/ShapeShape/multi_head_attention_2/attention_output/add:z:0*
T0*
_output_shapes
:�
.dropout_9/dropout/random_uniform/RandomUniformRandomUniform dropout_9/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0e
 dropout_9/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_9/dropout/GreaterEqualGreaterEqual7dropout_9/dropout/random_uniform/RandomUniform:output:0)dropout_9/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
dropout_9/dropout/CastCast"dropout_9/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
dropout_9/dropout/Mul_1Muldropout_9/dropout/Mul:z:0dropout_9/dropout/Cast:y:0*
T0*+
_output_shapes
:���������dg
addAddV2inputsdropout_9/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_4/moments/meanMeanadd:z:0=layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_4/moments/StopGradientStopGradient+layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_4/moments/SquaredDifferenceSquaredDifferenceadd:z:03layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_4/moments/varianceMean3layer_normalization_4/moments/SquaredDifference:z:0Alayer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_4/batchnorm/addAddV2/layer_normalization_4/moments/variance:output:0.layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/RsqrtRsqrt'layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/mulMul)layer_normalization_4/batchnorm/Rsqrt:y:0:layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_1Muladd:z:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_2Mul+layer_normalization_4/moments/mean:output:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_4/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/subSub6layer_normalization_4/batchnorm/ReadVariableOp:value:0)layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/add_1AddV2)layer_normalization_4/batchnorm/mul_1:z:0'layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       }
$sequential_2/dense_8/Tensordot/ShapeShape)layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:n
,sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/GatherV2GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/free:output:05sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_8/Tensordot/GatherV2_1GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/axes:output:07sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_8/Tensordot/ProdProd0sequential_2/dense_8/Tensordot/GatherV2:output:0-sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_8/Tensordot/Prod_1Prod2sequential_2/dense_8/Tensordot/GatherV2_1:output:0/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_8/Tensordot/concatConcatV2,sequential_2/dense_8/Tensordot/free:output:0,sequential_2/dense_8/Tensordot/axes:output:03sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_8/Tensordot/stackPack,sequential_2/dense_8/Tensordot/Prod:output:0.sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_8/Tensordot/transpose	Transpose)layer_normalization_4/batchnorm/add_1:z:0.sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_8/Tensordot/ReshapeReshape,sequential_2/dense_8/Tensordot/transpose:y:0-sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_8/Tensordot/MatMulMatMul/sequential_2/dense_8/Tensordot/Reshape:output:05sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/concat_1ConcatV20sequential_2/dense_8/Tensordot/GatherV2:output:0/sequential_2/dense_8/Tensordot/Const_2:output:05sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_8/TensordotReshape/sequential_2/dense_8/Tensordot/MatMul:product:00sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_8/BiasAddBiasAdd'sequential_2/dense_8/Tensordot:output:03sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d~
sequential_2/dense_8/ReluRelu%sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       {
$sequential_2/dense_9/Tensordot/ShapeShape'sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:n
,sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/GatherV2GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/free:output:05sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_9/Tensordot/GatherV2_1GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/axes:output:07sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_9/Tensordot/ProdProd0sequential_2/dense_9/Tensordot/GatherV2:output:0-sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_9/Tensordot/Prod_1Prod2sequential_2/dense_9/Tensordot/GatherV2_1:output:0/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_9/Tensordot/concatConcatV2,sequential_2/dense_9/Tensordot/free:output:0,sequential_2/dense_9/Tensordot/axes:output:03sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_9/Tensordot/stackPack,sequential_2/dense_9/Tensordot/Prod:output:0.sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_9/Tensordot/transpose	Transpose'sequential_2/dense_8/Relu:activations:0.sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_9/Tensordot/ReshapeReshape,sequential_2/dense_9/Tensordot/transpose:y:0-sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_9/Tensordot/MatMulMatMul/sequential_2/dense_9/Tensordot/Reshape:output:05sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/concat_1ConcatV20sequential_2/dense_9/Tensordot/GatherV2:output:0/sequential_2/dense_9/Tensordot/Const_2:output:05sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_9/TensordotReshape/sequential_2/dense_9/Tensordot/MatMul:product:00sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_9/BiasAddBiasAdd'sequential_2/dense_9/Tensordot:output:03sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d]
dropout_10/dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?�
dropout_10/dropout/MulMul%sequential_2/dense_9/BiasAdd:output:0!dropout_10/dropout/Const:output:0*
T0*+
_output_shapes
:���������dm
dropout_10/dropout/ShapeShape%sequential_2/dense_9/BiasAdd:output:0*
T0*
_output_shapes
:�
/dropout_10/dropout/random_uniform/RandomUniformRandomUniform!dropout_10/dropout/Shape:output:0*
T0*+
_output_shapes
:���������d*
dtype0f
!dropout_10/dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout_10/dropout/GreaterEqualGreaterEqual8dropout_10/dropout/random_uniform/RandomUniform:output:0*dropout_10/dropout/GreaterEqual/y:output:0*
T0*+
_output_shapes
:���������d�
dropout_10/dropout/CastCast#dropout_10/dropout/GreaterEqual:z:0*

DstT0*

SrcT0
*+
_output_shapes
:���������d�
dropout_10/dropout/Mul_1Muldropout_10/dropout/Mul:z:0dropout_10/dropout/Cast:y:0*
T0*+
_output_shapes
:���������d�
add_1AddV2)layer_normalization_4/batchnorm/add_1:z:0dropout_10/dropout/Mul_1:z:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_5/moments/meanMean	add_1:z:0=layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_5/moments/StopGradientStopGradient+layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_5/moments/SquaredDifferenceSquaredDifference	add_1:z:03layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_5/moments/varianceMean3layer_normalization_5/moments/SquaredDifference:z:0Alayer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_5/batchnorm/addAddV2/layer_normalization_5/moments/variance:output:0.layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/RsqrtRsqrt'layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/mulMul)layer_normalization_5/batchnorm/Rsqrt:y:0:layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_1Mul	add_1:z:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_2Mul+layer_normalization_5/moments/mean:output:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_5/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/subSub6layer_normalization_5/batchnorm/ReadVariableOp:value:0)layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/add_1AddV2)layer_normalization_5/batchnorm/mul_1:z:0'layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d|
IdentityIdentity)layer_normalization_5/batchnorm/add_1:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp/^layer_normalization_4/batchnorm/ReadVariableOp3^layer_normalization_4/batchnorm/mul/ReadVariableOp/^layer_normalization_5/batchnorm/ReadVariableOp3^layer_normalization_5/batchnorm/mul/ReadVariableOp;^multi_head_attention_2/attention_output/add/ReadVariableOpE^multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp.^multi_head_attention_2/key/add/ReadVariableOp8^multi_head_attention_2/key/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/query/add/ReadVariableOp:^multi_head_attention_2/query/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/value/add/ReadVariableOp:^multi_head_attention_2/value/einsum/Einsum/ReadVariableOp,^sequential_2/dense_8/BiasAdd/ReadVariableOp.^sequential_2/dense_8/Tensordot/ReadVariableOp,^sequential_2/dense_9/BiasAdd/ReadVariableOp.^sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 2`
.layer_normalization_4/batchnorm/ReadVariableOp.layer_normalization_4/batchnorm/ReadVariableOp2h
2layer_normalization_4/batchnorm/mul/ReadVariableOp2layer_normalization_4/batchnorm/mul/ReadVariableOp2`
.layer_normalization_5/batchnorm/ReadVariableOp.layer_normalization_5/batchnorm/ReadVariableOp2h
2layer_normalization_5/batchnorm/mul/ReadVariableOp2layer_normalization_5/batchnorm/mul/ReadVariableOp2x
:multi_head_attention_2/attention_output/add/ReadVariableOp:multi_head_attention_2/attention_output/add/ReadVariableOp2�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpDmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2^
-multi_head_attention_2/key/add/ReadVariableOp-multi_head_attention_2/key/add/ReadVariableOp2r
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/query/add/ReadVariableOp/multi_head_attention_2/query/add/ReadVariableOp2v
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/value/add/ReadVariableOp/multi_head_attention_2/value/add/ReadVariableOp2v
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2Z
+sequential_2/dense_8/BiasAdd/ReadVariableOp+sequential_2/dense_8/BiasAdd/ReadVariableOp2^
-sequential_2/dense_8/Tensordot/ReadVariableOp-sequential_2/dense_8/Tensordot/ReadVariableOp2Z
+sequential_2/dense_9/BiasAdd/ReadVariableOp+sequential_2/dense_9/BiasAdd/ReadVariableOp2^
-sequential_2/dense_9/Tensordot/ReadVariableOp-sequential_2/dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�

�
C__inference_dense_10_layer_call_and_return_conditional_losses_52901

inputs0
matmul_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�MatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:���������a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:���������w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
Ԣ
�+
__inference__traced_save_55040
file_prefix.
*savev2_dense_10_kernel_read_readvariableop,
(savev2_dense_10_bias_read_readvariableop.
*savev2_dense_11_kernel_read_readvariableop,
(savev2_dense_11_bias_read_readvariableopT
Psavev2_token_and_position_embedding_2_embedding_4_embeddings_read_readvariableopT
Psavev2_token_and_position_embedding_2_embedding_5_embeddings_read_readvariableopV
Rsavev2_transformer_block_2_multi_head_attention_2_query_kernel_read_readvariableopT
Psavev2_transformer_block_2_multi_head_attention_2_query_bias_read_readvariableopT
Psavev2_transformer_block_2_multi_head_attention_2_key_kernel_read_readvariableopR
Nsavev2_transformer_block_2_multi_head_attention_2_key_bias_read_readvariableopV
Rsavev2_transformer_block_2_multi_head_attention_2_value_kernel_read_readvariableopT
Psavev2_transformer_block_2_multi_head_attention_2_value_bias_read_readvariableopa
]savev2_transformer_block_2_multi_head_attention_2_attention_output_kernel_read_readvariableop_
[savev2_transformer_block_2_multi_head_attention_2_attention_output_bias_read_readvariableop-
)savev2_dense_8_kernel_read_readvariableop+
'savev2_dense_8_bias_read_readvariableop-
)savev2_dense_9_kernel_read_readvariableop+
'savev2_dense_9_bias_read_readvariableopN
Jsavev2_transformer_block_2_layer_normalization_4_gamma_read_readvariableopM
Isavev2_transformer_block_2_layer_normalization_4_beta_read_readvariableopN
Jsavev2_transformer_block_2_layer_normalization_5_gamma_read_readvariableopM
Isavev2_transformer_block_2_layer_normalization_5_beta_read_readvariableop(
$savev2_adam_iter_read_readvariableop	*
&savev2_adam_beta_1_read_readvariableop*
&savev2_adam_beta_2_read_readvariableop)
%savev2_adam_decay_read_readvariableop1
-savev2_adam_learning_rate_read_readvariableop&
"savev2_total_1_read_readvariableop&
"savev2_count_1_read_readvariableop$
 savev2_total_read_readvariableop$
 savev2_count_read_readvariableop5
1savev2_adam_dense_10_kernel_m_read_readvariableop3
/savev2_adam_dense_10_bias_m_read_readvariableop5
1savev2_adam_dense_11_kernel_m_read_readvariableop3
/savev2_adam_dense_11_bias_m_read_readvariableop[
Wsavev2_adam_token_and_position_embedding_2_embedding_4_embeddings_m_read_readvariableop[
Wsavev2_adam_token_and_position_embedding_2_embedding_5_embeddings_m_read_readvariableop]
Ysavev2_adam_transformer_block_2_multi_head_attention_2_query_kernel_m_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_query_bias_m_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_key_kernel_m_read_readvariableopY
Usavev2_adam_transformer_block_2_multi_head_attention_2_key_bias_m_read_readvariableop]
Ysavev2_adam_transformer_block_2_multi_head_attention_2_value_kernel_m_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_value_bias_m_read_readvariableoph
dsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_m_read_readvariableopf
bsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_m_read_readvariableop4
0savev2_adam_dense_8_kernel_m_read_readvariableop2
.savev2_adam_dense_8_bias_m_read_readvariableop4
0savev2_adam_dense_9_kernel_m_read_readvariableop2
.savev2_adam_dense_9_bias_m_read_readvariableopU
Qsavev2_adam_transformer_block_2_layer_normalization_4_gamma_m_read_readvariableopT
Psavev2_adam_transformer_block_2_layer_normalization_4_beta_m_read_readvariableopU
Qsavev2_adam_transformer_block_2_layer_normalization_5_gamma_m_read_readvariableopT
Psavev2_adam_transformer_block_2_layer_normalization_5_beta_m_read_readvariableop5
1savev2_adam_dense_10_kernel_v_read_readvariableop3
/savev2_adam_dense_10_bias_v_read_readvariableop5
1savev2_adam_dense_11_kernel_v_read_readvariableop3
/savev2_adam_dense_11_bias_v_read_readvariableop[
Wsavev2_adam_token_and_position_embedding_2_embedding_4_embeddings_v_read_readvariableop[
Wsavev2_adam_token_and_position_embedding_2_embedding_5_embeddings_v_read_readvariableop]
Ysavev2_adam_transformer_block_2_multi_head_attention_2_query_kernel_v_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_query_bias_v_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_key_kernel_v_read_readvariableopY
Usavev2_adam_transformer_block_2_multi_head_attention_2_key_bias_v_read_readvariableop]
Ysavev2_adam_transformer_block_2_multi_head_attention_2_value_kernel_v_read_readvariableop[
Wsavev2_adam_transformer_block_2_multi_head_attention_2_value_bias_v_read_readvariableoph
dsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_v_read_readvariableopf
bsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_v_read_readvariableop4
0savev2_adam_dense_8_kernel_v_read_readvariableop2
.savev2_adam_dense_8_bias_v_read_readvariableop4
0savev2_adam_dense_9_kernel_v_read_readvariableop2
.savev2_adam_dense_9_bias_v_read_readvariableopU
Qsavev2_adam_transformer_block_2_layer_normalization_4_gamma_v_read_readvariableopT
Psavev2_adam_transformer_block_2_layer_normalization_4_beta_v_read_readvariableopU
Qsavev2_adam_transformer_block_2_layer_normalization_5_gamma_v_read_readvariableopT
Psavev2_adam_transformer_block_2_layer_normalization_5_beta_v_read_readvariableop
savev2_const

identity_1��MergeV2Checkpointsw
StaticRegexFullMatchStaticRegexFullMatchfile_prefix"/device:CPU:**
_output_shapes
: *
pattern
^s3://.*Z
ConstConst"/device:CPU:**
_output_shapes
: *
dtype0*
valueB B.parta
Const_1Const"/device:CPU:**
_output_shapes
: *
dtype0*
valueB B
_temp/part�
SelectSelectStaticRegexFullMatch:output:0Const:output:0Const_1:output:0"/device:CPU:**
T0*
_output_shapes
: f

StringJoin
StringJoinfile_prefixSelect:output:0"/device:CPU:**
N*
_output_shapes
: L

num_shardsConst*
_output_shapes
: *
dtype0*
value	B :f
ShardedFilename/shardConst"/device:CPU:0*
_output_shapes
: *
dtype0*
value	B : �
ShardedFilenameShardedFilenameStringJoin:output:0ShardedFilename/shard:output:0num_shards:output:0"/device:CPU:0*
_output_shapes
: �$
SaveV2/tensor_namesConst"/device:CPU:0*
_output_shapes
:L*
dtype0*�#
value�#B�#LB6layer_with_weights-2/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-2/bias/.ATTRIBUTES/VARIABLE_VALUEB6layer_with_weights-3/kernel/.ATTRIBUTES/VARIABLE_VALUEB4layer_with_weights-3/bias/.ATTRIBUTES/VARIABLE_VALUEB&variables/0/.ATTRIBUTES/VARIABLE_VALUEB&variables/1/.ATTRIBUTES/VARIABLE_VALUEB&variables/2/.ATTRIBUTES/VARIABLE_VALUEB&variables/3/.ATTRIBUTES/VARIABLE_VALUEB&variables/4/.ATTRIBUTES/VARIABLE_VALUEB&variables/5/.ATTRIBUTES/VARIABLE_VALUEB&variables/6/.ATTRIBUTES/VARIABLE_VALUEB&variables/7/.ATTRIBUTES/VARIABLE_VALUEB&variables/8/.ATTRIBUTES/VARIABLE_VALUEB&variables/9/.ATTRIBUTES/VARIABLE_VALUEB'variables/10/.ATTRIBUTES/VARIABLE_VALUEB'variables/11/.ATTRIBUTES/VARIABLE_VALUEB'variables/12/.ATTRIBUTES/VARIABLE_VALUEB'variables/13/.ATTRIBUTES/VARIABLE_VALUEB'variables/14/.ATTRIBUTES/VARIABLE_VALUEB'variables/15/.ATTRIBUTES/VARIABLE_VALUEB'variables/16/.ATTRIBUTES/VARIABLE_VALUEB'variables/17/.ATTRIBUTES/VARIABLE_VALUEB)optimizer/iter/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_1/.ATTRIBUTES/VARIABLE_VALUEB+optimizer/beta_2/.ATTRIBUTES/VARIABLE_VALUEB*optimizer/decay/.ATTRIBUTES/VARIABLE_VALUEB2optimizer/learning_rate/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/0/count/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/total/.ATTRIBUTES/VARIABLE_VALUEB4keras_api/metrics/1/count/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/0/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/1/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/2/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/3/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/4/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/5/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/6/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/7/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/8/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBBvariables/9/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/10/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/11/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/12/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/13/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/14/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/15/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/16/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBCvariables/17/.OPTIMIZER_SLOT/optimizer/m/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-2/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-2/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBRlayer_with_weights-3/kernel/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBPlayer_with_weights-3/bias/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/0/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/1/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/2/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/3/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/4/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/5/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/6/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/7/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/8/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBBvariables/9/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/10/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/11/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/12/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/13/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/14/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/15/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/16/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEBCvariables/17/.OPTIMIZER_SLOT/optimizer/v/.ATTRIBUTES/VARIABLE_VALUEB_CHECKPOINTABLE_OBJECT_GRAPH�
SaveV2/shape_and_slicesConst"/device:CPU:0*
_output_shapes
:L*
dtype0*�
value�B�LB B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B B �)
SaveV2SaveV2ShardedFilename:filename:0SaveV2/tensor_names:output:0 SaveV2/shape_and_slices:output:0*savev2_dense_10_kernel_read_readvariableop(savev2_dense_10_bias_read_readvariableop*savev2_dense_11_kernel_read_readvariableop(savev2_dense_11_bias_read_readvariableopPsavev2_token_and_position_embedding_2_embedding_4_embeddings_read_readvariableopPsavev2_token_and_position_embedding_2_embedding_5_embeddings_read_readvariableopRsavev2_transformer_block_2_multi_head_attention_2_query_kernel_read_readvariableopPsavev2_transformer_block_2_multi_head_attention_2_query_bias_read_readvariableopPsavev2_transformer_block_2_multi_head_attention_2_key_kernel_read_readvariableopNsavev2_transformer_block_2_multi_head_attention_2_key_bias_read_readvariableopRsavev2_transformer_block_2_multi_head_attention_2_value_kernel_read_readvariableopPsavev2_transformer_block_2_multi_head_attention_2_value_bias_read_readvariableop]savev2_transformer_block_2_multi_head_attention_2_attention_output_kernel_read_readvariableop[savev2_transformer_block_2_multi_head_attention_2_attention_output_bias_read_readvariableop)savev2_dense_8_kernel_read_readvariableop'savev2_dense_8_bias_read_readvariableop)savev2_dense_9_kernel_read_readvariableop'savev2_dense_9_bias_read_readvariableopJsavev2_transformer_block_2_layer_normalization_4_gamma_read_readvariableopIsavev2_transformer_block_2_layer_normalization_4_beta_read_readvariableopJsavev2_transformer_block_2_layer_normalization_5_gamma_read_readvariableopIsavev2_transformer_block_2_layer_normalization_5_beta_read_readvariableop$savev2_adam_iter_read_readvariableop&savev2_adam_beta_1_read_readvariableop&savev2_adam_beta_2_read_readvariableop%savev2_adam_decay_read_readvariableop-savev2_adam_learning_rate_read_readvariableop"savev2_total_1_read_readvariableop"savev2_count_1_read_readvariableop savev2_total_read_readvariableop savev2_count_read_readvariableop1savev2_adam_dense_10_kernel_m_read_readvariableop/savev2_adam_dense_10_bias_m_read_readvariableop1savev2_adam_dense_11_kernel_m_read_readvariableop/savev2_adam_dense_11_bias_m_read_readvariableopWsavev2_adam_token_and_position_embedding_2_embedding_4_embeddings_m_read_readvariableopWsavev2_adam_token_and_position_embedding_2_embedding_5_embeddings_m_read_readvariableopYsavev2_adam_transformer_block_2_multi_head_attention_2_query_kernel_m_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_query_bias_m_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_key_kernel_m_read_readvariableopUsavev2_adam_transformer_block_2_multi_head_attention_2_key_bias_m_read_readvariableopYsavev2_adam_transformer_block_2_multi_head_attention_2_value_kernel_m_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_value_bias_m_read_readvariableopdsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_m_read_readvariableopbsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_m_read_readvariableop0savev2_adam_dense_8_kernel_m_read_readvariableop.savev2_adam_dense_8_bias_m_read_readvariableop0savev2_adam_dense_9_kernel_m_read_readvariableop.savev2_adam_dense_9_bias_m_read_readvariableopQsavev2_adam_transformer_block_2_layer_normalization_4_gamma_m_read_readvariableopPsavev2_adam_transformer_block_2_layer_normalization_4_beta_m_read_readvariableopQsavev2_adam_transformer_block_2_layer_normalization_5_gamma_m_read_readvariableopPsavev2_adam_transformer_block_2_layer_normalization_5_beta_m_read_readvariableop1savev2_adam_dense_10_kernel_v_read_readvariableop/savev2_adam_dense_10_bias_v_read_readvariableop1savev2_adam_dense_11_kernel_v_read_readvariableop/savev2_adam_dense_11_bias_v_read_readvariableopWsavev2_adam_token_and_position_embedding_2_embedding_4_embeddings_v_read_readvariableopWsavev2_adam_token_and_position_embedding_2_embedding_5_embeddings_v_read_readvariableopYsavev2_adam_transformer_block_2_multi_head_attention_2_query_kernel_v_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_query_bias_v_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_key_kernel_v_read_readvariableopUsavev2_adam_transformer_block_2_multi_head_attention_2_key_bias_v_read_readvariableopYsavev2_adam_transformer_block_2_multi_head_attention_2_value_kernel_v_read_readvariableopWsavev2_adam_transformer_block_2_multi_head_attention_2_value_bias_v_read_readvariableopdsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_kernel_v_read_readvariableopbsavev2_adam_transformer_block_2_multi_head_attention_2_attention_output_bias_v_read_readvariableop0savev2_adam_dense_8_kernel_v_read_readvariableop.savev2_adam_dense_8_bias_v_read_readvariableop0savev2_adam_dense_9_kernel_v_read_readvariableop.savev2_adam_dense_9_bias_v_read_readvariableopQsavev2_adam_transformer_block_2_layer_normalization_4_gamma_v_read_readvariableopPsavev2_adam_transformer_block_2_layer_normalization_4_beta_v_read_readvariableopQsavev2_adam_transformer_block_2_layer_normalization_5_gamma_v_read_readvariableopPsavev2_adam_transformer_block_2_layer_normalization_5_beta_v_read_readvariableopsavev2_const"/device:CPU:0*
_output_shapes
 *Z
dtypesP
N2L	�
&MergeV2Checkpoints/checkpoint_prefixesPackShardedFilename:filename:0^SaveV2"/device:CPU:0*
N*
T0*
_output_shapes
:�
MergeV2CheckpointsMergeV2Checkpoints/MergeV2Checkpoints/checkpoint_prefixes:output:0file_prefix"/device:CPU:0*
_output_shapes
 f
IdentityIdentityfile_prefix^MergeV2Checkpoints"/device:CPU:0*
T0*
_output_shapes
: Q

Identity_1IdentityIdentity:output:0^NoOp*
T0*
_output_shapes
: [
NoOpNoOp^MergeV2Checkpoints*"
_acd_function_control_output(*
_output_shapes
 "!

identity_1Identity_1:output:0*�
_input_shapes�
�: :::::	�:d::::::::::::::::: : : : : : : : : :::::	�:d:::::::::::::::::::::	�:d::::::::::::::::: 2(
MergeV2CheckpointsMergeV2Checkpoints:C ?

_output_shapes
: 
%
_user_specified_namefile_prefix:$ 

_output_shapes

:: 

_output_shapes
::$ 

_output_shapes

:: 

_output_shapes
::%!

_output_shapes
:	�:$ 

_output_shapes

:d:($
"
_output_shapes
::$ 

_output_shapes

::(	$
"
_output_shapes
::$
 

_output_shapes

::($
"
_output_shapes
::$ 

_output_shapes

::($
"
_output_shapes
:: 

_output_shapes
::$ 

_output_shapes

:: 

_output_shapes
::$ 

_output_shapes

:: 

_output_shapes
:: 

_output_shapes
:: 

_output_shapes
:: 

_output_shapes
:: 

_output_shapes
::

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :

_output_shapes
: :$  

_output_shapes

:: !

_output_shapes
::$" 

_output_shapes

:: #

_output_shapes
::%$!

_output_shapes
:	�:$% 

_output_shapes

:d:(&$
"
_output_shapes
::$' 

_output_shapes

::(($
"
_output_shapes
::$) 

_output_shapes

::(*$
"
_output_shapes
::$+ 

_output_shapes

::(,$
"
_output_shapes
:: -

_output_shapes
::$. 

_output_shapes

:: /

_output_shapes
::$0 

_output_shapes

:: 1

_output_shapes
:: 2

_output_shapes
:: 3

_output_shapes
:: 4

_output_shapes
:: 5

_output_shapes
::$6 

_output_shapes

:: 7

_output_shapes
::$8 

_output_shapes

:: 9

_output_shapes
::%:!

_output_shapes
:	�:$; 

_output_shapes

:d:(<$
"
_output_shapes
::$= 

_output_shapes

::(>$
"
_output_shapes
::$? 

_output_shapes

::(@$
"
_output_shapes
::$A 

_output_shapes

::(B$
"
_output_shapes
:: C

_output_shapes
::$D 

_output_shapes

:: E

_output_shapes
::$F 

_output_shapes

:: G

_output_shapes
:: H

_output_shapes
:: I

_output_shapes
:: J

_output_shapes
:: K

_output_shapes
::L

_output_shapes
: 
�
q
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_54479

inputs
identityX
Mean/reduction_indicesConst*
_output_shapes
: *
dtype0*
value	B :p
MeanMeaninputsMean/reduction_indices:output:0*
T0*0
_output_shapes
:������������������^
IdentityIdentityMean:output:0*
T0*0
_output_shapes
:������������������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*<
_input_shapes+
):'���������������������������:e a
=
_output_shapes+
):'���������������������������
 
_user_specified_nameinputs
�

�
C__inference_dense_11_layer_call_and_return_conditional_losses_52925

inputs0
matmul_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�MatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������V
SoftmaxSoftmaxBiasAdd:output:0*
T0*'
_output_shapes
:���������`
IdentityIdentitySoftmax:softmax:0^NoOp*
T0*'
_output_shapes
:���������w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�-
�

B__inference_model_2_layer_call_and_return_conditional_losses_53376

inputs6
$token_and_position_embedding_2_53324:d7
$token_and_position_embedding_2_53326:	�/
transformer_block_2_53329:+
transformer_block_2_53331:/
transformer_block_2_53333:+
transformer_block_2_53335:/
transformer_block_2_53337:+
transformer_block_2_53339:/
transformer_block_2_53341:'
transformer_block_2_53343:'
transformer_block_2_53345:'
transformer_block_2_53347:+
transformer_block_2_53349:'
transformer_block_2_53351:+
transformer_block_2_53353:'
transformer_block_2_53355:'
transformer_block_2_53357:'
transformer_block_2_53359: 
dense_10_53364:
dense_10_53366: 
dense_11_53370:
dense_11_53372:
identity�� dense_10/StatefulPartitionedCall� dense_11/StatefulPartitionedCall�"dropout_11/StatefulPartitionedCall�"dropout_12/StatefulPartitionedCall�6token_and_position_embedding_2/StatefulPartitionedCall�+transformer_block_2/StatefulPartitionedCall�
6token_and_position_embedding_2/StatefulPartitionedCallStatefulPartitionedCallinputs$token_and_position_embedding_2_53324$token_and_position_embedding_2_53326*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *b
f]R[
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715�
+transformer_block_2/StatefulPartitionedCallStatefulPartitionedCall?token_and_position_embedding_2/StatefulPartitionedCall:output:0transformer_block_2_53329transformer_block_2_53331transformer_block_2_53333transformer_block_2_53335transformer_block_2_53337transformer_block_2_53339transformer_block_2_53341transformer_block_2_53343transformer_block_2_53345transformer_block_2_53347transformer_block_2_53349transformer_block_2_53351transformer_block_2_53353transformer_block_2_53355transformer_block_2_53357transformer_block_2_53359*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_53225�
*global_average_pooling1d_2/PartitionedCallPartitionedCall4transformer_block_2/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *^
fYRW
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681�
"dropout_11/StatefulPartitionedCallStatefulPartitionedCall3global_average_pooling1d_2/PartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_53042�
 dense_10/StatefulPartitionedCallStatefulPartitionedCall+dropout_11/StatefulPartitionedCall:output:0dense_10_53364dense_10_53366*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_10_layer_call_and_return_conditional_losses_52901�
"dropout_12/StatefulPartitionedCallStatefulPartitionedCall)dense_10/StatefulPartitionedCall:output:0#^dropout_11/StatefulPartitionedCall*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_53009�
 dense_11/StatefulPartitionedCallStatefulPartitionedCall+dropout_12/StatefulPartitionedCall:output:0dense_11_53370dense_11_53372*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_11_layer_call_and_return_conditional_losses_52925x
IdentityIdentity)dense_11/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp!^dense_10/StatefulPartitionedCall!^dense_11/StatefulPartitionedCall#^dropout_11/StatefulPartitionedCall#^dropout_12/StatefulPartitionedCall7^token_and_position_embedding_2/StatefulPartitionedCall,^transformer_block_2/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2D
 dense_10/StatefulPartitionedCall dense_10/StatefulPartitionedCall2D
 dense_11/StatefulPartitionedCall dense_11/StatefulPartitionedCall2H
"dropout_11/StatefulPartitionedCall"dropout_11/StatefulPartitionedCall2H
"dropout_12/StatefulPartitionedCall"dropout_12/StatefulPartitionedCall2p
6token_and_position_embedding_2/StatefulPartitionedCall6token_and_position_embedding_2/StatefulPartitionedCall2Z
+transformer_block_2/StatefulPartitionedCall+transformer_block_2/StatefulPartitionedCall:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
'__inference_model_2_layer_call_fn_53688

inputs
unknown:d
	unknown_0:	�
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:

unknown_15:

unknown_16:

unknown_17:

unknown_18:

unknown_19:

unknown_20:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14
unknown_15
unknown_16
unknown_17
unknown_18
unknown_19
unknown_20*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_model_2_layer_call_and_return_conditional_losses_52932o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�
F
*__inference_dropout_11_layer_call_fn_54484

inputs
identity�
PartitionedCallPartitionedCallinputs*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_52888`
IdentityIdentityPartitionedCall:output:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
c
*__inference_dropout_11_layer_call_fn_54489

inputs
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputs*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_53042o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
>__inference_token_and_position_embedding_2_layer_call_fn_54103
x
unknown:d
	unknown_0:	�
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallxunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *b
f]R[
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������d: : 22
StatefulPartitionedCallStatefulPartitionedCall:J F
'
_output_shapes
:���������d

_user_specified_namex
�
�
,__inference_sequential_2_layer_call_fn_52643
dense_8_input
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCalldense_8_inputunknown	unknown_0	unknown_1	unknown_2*
Tin	
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*&
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *P
fKRI
G__inference_sequential_2_layer_call_and_return_conditional_losses_52619s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 22
StatefulPartitionedCallStatefulPartitionedCall:Z V
+
_output_shapes
:���������d
'
_user_specified_namedense_8_input
�
�
B__inference_dense_8_layer_call_and_return_conditional_losses_52516

inputs3
!tensordot_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�Tensordot/ReadVariableOpz
Tensordot/ReadVariableOpReadVariableOp!tensordot_readvariableop_resource*
_output_shapes

:*
dtype0X
Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:_
Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       E
Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:Y
Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2GatherV2Tensordot/Shape:output:0Tensordot/free:output:0 Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:[
Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2_1GatherV2Tensordot/Shape:output:0Tensordot/axes:output:0"Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:Y
Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: n
Tensordot/ProdProdTensordot/GatherV2:output:0Tensordot/Const:output:0*
T0*
_output_shapes
: [
Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: t
Tensordot/Prod_1ProdTensordot/GatherV2_1:output:0Tensordot/Const_1:output:0*
T0*
_output_shapes
: W
Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concatConcatV2Tensordot/free:output:0Tensordot/axes:output:0Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:y
Tensordot/stackPackTensordot/Prod:output:0Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:y
Tensordot/transpose	TransposeinputsTensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Tensordot/ReshapeReshapeTensordot/transpose:y:0Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Tensordot/MatMulMatMulTensordot/Reshape:output:0 Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������[
Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:Y
Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concat_1ConcatV2Tensordot/GatherV2:output:0Tensordot/Const_2:output:0 Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
	TensordotReshapeTensordot/MatMul:product:0Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������dr
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0|
BiasAddBiasAddTensordot:output:0BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dT
ReluReluBiasAdd:output:0*
T0*+
_output_shapes
:���������de
IdentityIdentityRelu:activations:0^NoOp*
T0*+
_output_shapes
:���������dz
NoOpNoOp^BiasAdd/ReadVariableOp^Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp24
Tensordot/ReadVariableOpTensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�*
�	
B__inference_model_2_layer_call_and_return_conditional_losses_53527
input_36
$token_and_position_embedding_2_53475:d7
$token_and_position_embedding_2_53477:	�/
transformer_block_2_53480:+
transformer_block_2_53482:/
transformer_block_2_53484:+
transformer_block_2_53486:/
transformer_block_2_53488:+
transformer_block_2_53490:/
transformer_block_2_53492:'
transformer_block_2_53494:'
transformer_block_2_53496:'
transformer_block_2_53498:+
transformer_block_2_53500:'
transformer_block_2_53502:+
transformer_block_2_53504:'
transformer_block_2_53506:'
transformer_block_2_53508:'
transformer_block_2_53510: 
dense_10_53515:
dense_10_53517: 
dense_11_53521:
dense_11_53523:
identity�� dense_10/StatefulPartitionedCall� dense_11/StatefulPartitionedCall�6token_and_position_embedding_2/StatefulPartitionedCall�+transformer_block_2/StatefulPartitionedCall�
6token_and_position_embedding_2/StatefulPartitionedCallStatefulPartitionedCallinput_3$token_and_position_embedding_2_53475$token_and_position_embedding_2_53477*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *b
f]R[
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715�
+transformer_block_2/StatefulPartitionedCallStatefulPartitionedCall?token_and_position_embedding_2/StatefulPartitionedCall:output:0transformer_block_2_53480transformer_block_2_53482transformer_block_2_53484transformer_block_2_53486transformer_block_2_53488transformer_block_2_53490transformer_block_2_53492transformer_block_2_53494transformer_block_2_53496transformer_block_2_53498transformer_block_2_53500transformer_block_2_53502transformer_block_2_53504transformer_block_2_53506transformer_block_2_53508transformer_block_2_53510*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_52848�
*global_average_pooling1d_2/PartitionedCallPartitionedCall4transformer_block_2/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *^
fYRW
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681�
dropout_11/PartitionedCallPartitionedCall3global_average_pooling1d_2/PartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_52888�
 dense_10/StatefulPartitionedCallStatefulPartitionedCall#dropout_11/PartitionedCall:output:0dense_10_53515dense_10_53517*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_10_layer_call_and_return_conditional_losses_52901�
dropout_12/PartitionedCallPartitionedCall)dense_10/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_52912�
 dense_11/StatefulPartitionedCallStatefulPartitionedCall#dropout_12/PartitionedCall:output:0dense_11_53521dense_11_53523*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_11_layer_call_and_return_conditional_losses_52925x
IdentityIdentity)dense_11/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp!^dense_10/StatefulPartitionedCall!^dense_11/StatefulPartitionedCall7^token_and_position_embedding_2/StatefulPartitionedCall,^transformer_block_2/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2D
 dense_10/StatefulPartitionedCall dense_10/StatefulPartitionedCall2D
 dense_11/StatefulPartitionedCall dense_11/StatefulPartitionedCall2p
6token_and_position_embedding_2/StatefulPartitionedCall6token_and_position_embedding_2/StatefulPartitionedCall2Z
+transformer_block_2/StatefulPartitionedCall+transformer_block_2/StatefulPartitionedCall:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
�
�
'__inference_model_2_layer_call_fn_52979
input_3
unknown:d
	unknown_0:	�
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:

unknown_15:

unknown_16:

unknown_17:

unknown_18:

unknown_19:

unknown_20:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinput_3unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14
unknown_15
unknown_16
unknown_17
unknown_18
unknown_19
unknown_20*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_model_2_layer_call_and_return_conditional_losses_52932o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
��
�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54328

inputsX
Bmulti_head_attention_2_query_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_query_add_readvariableop_resource:V
@multi_head_attention_2_key_einsum_einsum_readvariableop_resource:H
6multi_head_attention_2_key_add_readvariableop_resource:X
Bmulti_head_attention_2_value_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_value_add_readvariableop_resource:c
Mmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:Q
Cmulti_head_attention_2_attention_output_add_readvariableop_resource:I
;layer_normalization_4_batchnorm_mul_readvariableop_resource:E
7layer_normalization_4_batchnorm_readvariableop_resource:H
6sequential_2_dense_8_tensordot_readvariableop_resource:B
4sequential_2_dense_8_biasadd_readvariableop_resource:H
6sequential_2_dense_9_tensordot_readvariableop_resource:B
4sequential_2_dense_9_biasadd_readvariableop_resource:I
;layer_normalization_5_batchnorm_mul_readvariableop_resource:E
7layer_normalization_5_batchnorm_readvariableop_resource:
identity��.layer_normalization_4/batchnorm/ReadVariableOp�2layer_normalization_4/batchnorm/mul/ReadVariableOp�.layer_normalization_5/batchnorm/ReadVariableOp�2layer_normalization_5/batchnorm/mul/ReadVariableOp�:multi_head_attention_2/attention_output/add/ReadVariableOp�Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�-multi_head_attention_2/key/add/ReadVariableOp�7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/query/add/ReadVariableOp�9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/value/add/ReadVariableOp�9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�+sequential_2/dense_8/BiasAdd/ReadVariableOp�-sequential_2/dense_8/Tensordot/ReadVariableOp�+sequential_2/dense_9/BiasAdd/ReadVariableOp�-sequential_2/dense_9/Tensordot/ReadVariableOp�
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/query/einsum/EinsumEinsuminputsAmulti_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/query/add/ReadVariableOpReadVariableOp8multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/query/addAddV23multi_head_attention_2/query/einsum/Einsum:output:07multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOp@multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
(multi_head_attention_2/key/einsum/EinsumEinsuminputs?multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
-multi_head_attention_2/key/add/ReadVariableOpReadVariableOp6multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
multi_head_attention_2/key/addAddV21multi_head_attention_2/key/einsum/Einsum:output:05multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/value/einsum/EinsumEinsuminputsAmulti_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/value/add/ReadVariableOpReadVariableOp8multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/value/addAddV23multi_head_attention_2/value/einsum/Einsum:output:07multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������da
multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
multi_head_attention_2/MulMul$multi_head_attention_2/query/add:z:0%multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
$multi_head_attention_2/einsum/EinsumEinsum"multi_head_attention_2/key/add:z:0multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
&multi_head_attention_2/softmax/SoftmaxSoftmax-multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
'multi_head_attention_2/dropout/IdentityIdentity0multi_head_attention_2/softmax/Softmax:softmax:0*
T0*/
_output_shapes
:���������dd�
&multi_head_attention_2/einsum_1/EinsumEinsum0multi_head_attention_2/dropout/Identity:output:0$multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpMmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
5multi_head_attention_2/attention_output/einsum/EinsumEinsum/multi_head_attention_2/einsum_1/Einsum:output:0Lmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
:multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpCmulti_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
+multi_head_attention_2/attention_output/addAddV2>multi_head_attention_2/attention_output/einsum/Einsum:output:0Bmulti_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
dropout_9/IdentityIdentity/multi_head_attention_2/attention_output/add:z:0*
T0*+
_output_shapes
:���������dg
addAddV2inputsdropout_9/Identity:output:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_4/moments/meanMeanadd:z:0=layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_4/moments/StopGradientStopGradient+layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_4/moments/SquaredDifferenceSquaredDifferenceadd:z:03layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_4/moments/varianceMean3layer_normalization_4/moments/SquaredDifference:z:0Alayer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_4/batchnorm/addAddV2/layer_normalization_4/moments/variance:output:0.layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/RsqrtRsqrt'layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/mulMul)layer_normalization_4/batchnorm/Rsqrt:y:0:layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_1Muladd:z:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_2Mul+layer_normalization_4/moments/mean:output:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_4/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/subSub6layer_normalization_4/batchnorm/ReadVariableOp:value:0)layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/add_1AddV2)layer_normalization_4/batchnorm/mul_1:z:0'layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       }
$sequential_2/dense_8/Tensordot/ShapeShape)layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:n
,sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/GatherV2GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/free:output:05sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_8/Tensordot/GatherV2_1GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/axes:output:07sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_8/Tensordot/ProdProd0sequential_2/dense_8/Tensordot/GatherV2:output:0-sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_8/Tensordot/Prod_1Prod2sequential_2/dense_8/Tensordot/GatherV2_1:output:0/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_8/Tensordot/concatConcatV2,sequential_2/dense_8/Tensordot/free:output:0,sequential_2/dense_8/Tensordot/axes:output:03sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_8/Tensordot/stackPack,sequential_2/dense_8/Tensordot/Prod:output:0.sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_8/Tensordot/transpose	Transpose)layer_normalization_4/batchnorm/add_1:z:0.sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_8/Tensordot/ReshapeReshape,sequential_2/dense_8/Tensordot/transpose:y:0-sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_8/Tensordot/MatMulMatMul/sequential_2/dense_8/Tensordot/Reshape:output:05sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/concat_1ConcatV20sequential_2/dense_8/Tensordot/GatherV2:output:0/sequential_2/dense_8/Tensordot/Const_2:output:05sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_8/TensordotReshape/sequential_2/dense_8/Tensordot/MatMul:product:00sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_8/BiasAddBiasAdd'sequential_2/dense_8/Tensordot:output:03sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d~
sequential_2/dense_8/ReluRelu%sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       {
$sequential_2/dense_9/Tensordot/ShapeShape'sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:n
,sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/GatherV2GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/free:output:05sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_9/Tensordot/GatherV2_1GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/axes:output:07sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_9/Tensordot/ProdProd0sequential_2/dense_9/Tensordot/GatherV2:output:0-sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_9/Tensordot/Prod_1Prod2sequential_2/dense_9/Tensordot/GatherV2_1:output:0/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_9/Tensordot/concatConcatV2,sequential_2/dense_9/Tensordot/free:output:0,sequential_2/dense_9/Tensordot/axes:output:03sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_9/Tensordot/stackPack,sequential_2/dense_9/Tensordot/Prod:output:0.sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_9/Tensordot/transpose	Transpose'sequential_2/dense_8/Relu:activations:0.sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_9/Tensordot/ReshapeReshape,sequential_2/dense_9/Tensordot/transpose:y:0-sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_9/Tensordot/MatMulMatMul/sequential_2/dense_9/Tensordot/Reshape:output:05sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/concat_1ConcatV20sequential_2/dense_9/Tensordot/GatherV2:output:0/sequential_2/dense_9/Tensordot/Const_2:output:05sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_9/TensordotReshape/sequential_2/dense_9/Tensordot/MatMul:product:00sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_9/BiasAddBiasAdd'sequential_2/dense_9/Tensordot:output:03sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d|
dropout_10/IdentityIdentity%sequential_2/dense_9/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
add_1AddV2)layer_normalization_4/batchnorm/add_1:z:0dropout_10/Identity:output:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_5/moments/meanMean	add_1:z:0=layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_5/moments/StopGradientStopGradient+layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_5/moments/SquaredDifferenceSquaredDifference	add_1:z:03layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_5/moments/varianceMean3layer_normalization_5/moments/SquaredDifference:z:0Alayer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_5/batchnorm/addAddV2/layer_normalization_5/moments/variance:output:0.layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/RsqrtRsqrt'layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/mulMul)layer_normalization_5/batchnorm/Rsqrt:y:0:layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_1Mul	add_1:z:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_2Mul+layer_normalization_5/moments/mean:output:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_5/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/subSub6layer_normalization_5/batchnorm/ReadVariableOp:value:0)layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/add_1AddV2)layer_normalization_5/batchnorm/mul_1:z:0'layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d|
IdentityIdentity)layer_normalization_5/batchnorm/add_1:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp/^layer_normalization_4/batchnorm/ReadVariableOp3^layer_normalization_4/batchnorm/mul/ReadVariableOp/^layer_normalization_5/batchnorm/ReadVariableOp3^layer_normalization_5/batchnorm/mul/ReadVariableOp;^multi_head_attention_2/attention_output/add/ReadVariableOpE^multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp.^multi_head_attention_2/key/add/ReadVariableOp8^multi_head_attention_2/key/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/query/add/ReadVariableOp:^multi_head_attention_2/query/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/value/add/ReadVariableOp:^multi_head_attention_2/value/einsum/Einsum/ReadVariableOp,^sequential_2/dense_8/BiasAdd/ReadVariableOp.^sequential_2/dense_8/Tensordot/ReadVariableOp,^sequential_2/dense_9/BiasAdd/ReadVariableOp.^sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 2`
.layer_normalization_4/batchnorm/ReadVariableOp.layer_normalization_4/batchnorm/ReadVariableOp2h
2layer_normalization_4/batchnorm/mul/ReadVariableOp2layer_normalization_4/batchnorm/mul/ReadVariableOp2`
.layer_normalization_5/batchnorm/ReadVariableOp.layer_normalization_5/batchnorm/ReadVariableOp2h
2layer_normalization_5/batchnorm/mul/ReadVariableOp2layer_normalization_5/batchnorm/mul/ReadVariableOp2x
:multi_head_attention_2/attention_output/add/ReadVariableOp:multi_head_attention_2/attention_output/add/ReadVariableOp2�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpDmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2^
-multi_head_attention_2/key/add/ReadVariableOp-multi_head_attention_2/key/add/ReadVariableOp2r
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/query/add/ReadVariableOp/multi_head_attention_2/query/add/ReadVariableOp2v
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/value/add/ReadVariableOp/multi_head_attention_2/value/add/ReadVariableOp2v
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2Z
+sequential_2/dense_8/BiasAdd/ReadVariableOp+sequential_2/dense_8/BiasAdd/ReadVariableOp2^
-sequential_2/dense_8/Tensordot/ReadVariableOp-sequential_2/dense_8/Tensordot/ReadVariableOp2Z
+sequential_2/dense_9/BiasAdd/ReadVariableOp+sequential_2/dense_9/BiasAdd/ReadVariableOp2^
-sequential_2/dense_9/Tensordot/ReadVariableOp-sequential_2/dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
c
E__inference_dropout_12_layer_call_and_return_conditional_losses_52912

inputs

identity_1N
IdentityIdentityinputs*
T0*'
_output_shapes
:���������[

Identity_1IdentityIdentity:output:0*
T0*'
_output_shapes
:���������"!

identity_1Identity_1:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
'__inference_model_2_layer_call_fn_53472
input_3
unknown:d
	unknown_0:	�
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:

unknown_15:

unknown_16:

unknown_17:

unknown_18:

unknown_19:

unknown_20:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinput_3unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14
unknown_15
unknown_16
unknown_17
unknown_18
unknown_19
unknown_20*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_model_2_layer_call_and_return_conditional_losses_53376o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
�
c
E__inference_dropout_11_layer_call_and_return_conditional_losses_52888

inputs

identity_1N
IdentityIdentityinputs*
T0*'
_output_shapes
:���������[

Identity_1IdentityIdentity:output:0*
T0*'
_output_shapes
:���������"!

identity_1Identity_1:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52657
dense_8_input
dense_8_52646:
dense_8_52648:
dense_9_52651:
dense_9_52653:
identity��dense_8/StatefulPartitionedCall�dense_9/StatefulPartitionedCall�
dense_8/StatefulPartitionedCallStatefulPartitionedCalldense_8_inputdense_8_52646dense_8_52648*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_8_layer_call_and_return_conditional_losses_52516�
dense_9/StatefulPartitionedCallStatefulPartitionedCall(dense_8/StatefulPartitionedCall:output:0dense_9_52651dense_9_52653*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_9_layer_call_and_return_conditional_losses_52552{
IdentityIdentity(dense_9/StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp ^dense_8/StatefulPartitionedCall ^dense_9/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2B
dense_8/StatefulPartitionedCalldense_8/StatefulPartitionedCall2B
dense_9/StatefulPartitionedCalldense_9/StatefulPartitionedCall:Z V
+
_output_shapes
:���������d
'
_user_specified_namedense_8_input
�
�
'__inference_model_2_layer_call_fn_53737

inputs
unknown:d
	unknown_0:	�
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:

unknown_15:

unknown_16:

unknown_17:

unknown_18:

unknown_19:

unknown_20:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14
unknown_15
unknown_16
unknown_17
unknown_18
unknown_19
unknown_20*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_model_2_layer_call_and_return_conditional_losses_53376o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_54127
x4
"embedding_5_embedding_lookup_54114:d5
"embedding_4_embedding_lookup_54120:	�
identity��embedding_4/embedding_lookup�embedding_5/embedding_lookup6
ShapeShapex*
T0*
_output_shapes
:f
strided_slice/stackConst*
_output_shapes
:*
dtype0*
valueB:
���������_
strided_slice/stack_1Const*
_output_shapes
:*
dtype0*
valueB: _
strided_slice/stack_2Const*
_output_shapes
:*
dtype0*
valueB:�
strided_sliceStridedSliceShape:output:0strided_slice/stack:output:0strided_slice/stack_1:output:0strided_slice/stack_2:output:0*
Index0*
T0*
_output_shapes
: *
shrink_axis_maskM
range/startConst*
_output_shapes
: *
dtype0*
value	B : M
range/deltaConst*
_output_shapes
: *
dtype0*
value	B :n
rangeRangerange/start:output:0strided_slice:output:0range/delta:output:0*
_output_shapes
:d�
embedding_5/embedding_lookupResourceGather"embedding_5_embedding_lookup_54114range:output:0*
Tindices0*5
_class+
)'loc:@embedding_5/embedding_lookup/54114*
_output_shapes

:d*
dtype0�
%embedding_5/embedding_lookup/IdentityIdentity%embedding_5/embedding_lookup:output:0*
T0*5
_class+
)'loc:@embedding_5/embedding_lookup/54114*
_output_shapes

:d�
'embedding_5/embedding_lookup/Identity_1Identity.embedding_5/embedding_lookup/Identity:output:0*
T0*
_output_shapes

:d\
embedding_4/CastCastx*

DstT0*

SrcT0*'
_output_shapes
:���������d�
embedding_4/embedding_lookupResourceGather"embedding_4_embedding_lookup_54120embedding_4/Cast:y:0*
Tindices0*5
_class+
)'loc:@embedding_4/embedding_lookup/54120*+
_output_shapes
:���������d*
dtype0�
%embedding_4/embedding_lookup/IdentityIdentity%embedding_4/embedding_lookup:output:0*
T0*5
_class+
)'loc:@embedding_4/embedding_lookup/54120*+
_output_shapes
:���������d�
'embedding_4/embedding_lookup/Identity_1Identity.embedding_4/embedding_lookup/Identity:output:0*
T0*+
_output_shapes
:���������d�
addAddV20embedding_4/embedding_lookup/Identity_1:output:00embedding_5/embedding_lookup/Identity_1:output:0*
T0*+
_output_shapes
:���������dZ
IdentityIdentityadd:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp^embedding_4/embedding_lookup^embedding_5/embedding_lookup*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������d: : 2<
embedding_4/embedding_lookupembedding_4/embedding_lookup2<
embedding_5/embedding_lookupembedding_5/embedding_lookup:J F
'
_output_shapes
:���������d

_user_specified_namex
�	
d
E__inference_dropout_12_layer_call_and_return_conditional_losses_54553

inputs
identity�R
dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?d
dropout/MulMulinputsdropout/Const:output:0*
T0*'
_output_shapes
:���������C
dropout/ShapeShapeinputs*
T0*
_output_shapes
:�
$dropout/random_uniform/RandomUniformRandomUniformdropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0[
dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout/GreaterEqualGreaterEqual-dropout/random_uniform/RandomUniform:output:0dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:���������o
dropout/CastCastdropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:���������i
dropout/Mul_1Muldropout/Mul:z:0dropout/Cast:y:0*
T0*'
_output_shapes
:���������Y
IdentityIdentitydropout/Mul_1:z:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
��
�
B__inference_model_2_layer_call_and_return_conditional_losses_53902

inputsS
Atoken_and_position_embedding_2_embedding_5_embedding_lookup_53748:dT
Atoken_and_position_embedding_2_embedding_4_embedding_lookup_53754:	�l
Vtransformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource:^
Ltransformer_block_2_multi_head_attention_2_query_add_readvariableop_resource:j
Ttransformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource:\
Jtransformer_block_2_multi_head_attention_2_key_add_readvariableop_resource:l
Vtransformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource:^
Ltransformer_block_2_multi_head_attention_2_value_add_readvariableop_resource:w
atransformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:e
Wtransformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource:]
Otransformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource:Y
Ktransformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource:\
Jtransformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource:V
Htransformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource:\
Jtransformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource:V
Htransformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource:]
Otransformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource:Y
Ktransformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource:9
'dense_10_matmul_readvariableop_resource:6
(dense_10_biasadd_readvariableop_resource:9
'dense_11_matmul_readvariableop_resource:6
(dense_11_biasadd_readvariableop_resource:
identity��dense_10/BiasAdd/ReadVariableOp�dense_10/MatMul/ReadVariableOp�dense_11/BiasAdd/ReadVariableOp�dense_11/MatMul/ReadVariableOp�;token_and_position_embedding_2/embedding_4/embedding_lookup�;token_and_position_embedding_2/embedding_5/embedding_lookup�Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp�Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp�Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp�Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp�Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp�Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp�Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp�Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp�Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp�Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp�?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp�Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpZ
$token_and_position_embedding_2/ShapeShapeinputs*
T0*
_output_shapes
:�
2token_and_position_embedding_2/strided_slice/stackConst*
_output_shapes
:*
dtype0*
valueB:
���������~
4token_and_position_embedding_2/strided_slice/stack_1Const*
_output_shapes
:*
dtype0*
valueB: ~
4token_and_position_embedding_2/strided_slice/stack_2Const*
_output_shapes
:*
dtype0*
valueB:�
,token_and_position_embedding_2/strided_sliceStridedSlice-token_and_position_embedding_2/Shape:output:0;token_and_position_embedding_2/strided_slice/stack:output:0=token_and_position_embedding_2/strided_slice/stack_1:output:0=token_and_position_embedding_2/strided_slice/stack_2:output:0*
Index0*
T0*
_output_shapes
: *
shrink_axis_maskl
*token_and_position_embedding_2/range/startConst*
_output_shapes
: *
dtype0*
value	B : l
*token_and_position_embedding_2/range/deltaConst*
_output_shapes
: *
dtype0*
value	B :�
$token_and_position_embedding_2/rangeRange3token_and_position_embedding_2/range/start:output:05token_and_position_embedding_2/strided_slice:output:03token_and_position_embedding_2/range/delta:output:0*
_output_shapes
:d�
;token_and_position_embedding_2/embedding_5/embedding_lookupResourceGatherAtoken_and_position_embedding_2_embedding_5_embedding_lookup_53748-token_and_position_embedding_2/range:output:0*
Tindices0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_5/embedding_lookup/53748*
_output_shapes

:d*
dtype0�
Dtoken_and_position_embedding_2/embedding_5/embedding_lookup/IdentityIdentityDtoken_and_position_embedding_2/embedding_5/embedding_lookup:output:0*
T0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_5/embedding_lookup/53748*
_output_shapes

:d�
Ftoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1IdentityMtoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity:output:0*
T0*
_output_shapes

:d�
/token_and_position_embedding_2/embedding_4/CastCastinputs*

DstT0*

SrcT0*'
_output_shapes
:���������d�
;token_and_position_embedding_2/embedding_4/embedding_lookupResourceGatherAtoken_and_position_embedding_2_embedding_4_embedding_lookup_537543token_and_position_embedding_2/embedding_4/Cast:y:0*
Tindices0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_4/embedding_lookup/53754*+
_output_shapes
:���������d*
dtype0�
Dtoken_and_position_embedding_2/embedding_4/embedding_lookup/IdentityIdentityDtoken_and_position_embedding_2/embedding_4/embedding_lookup:output:0*
T0*T
_classJ
HFloc:@token_and_position_embedding_2/embedding_4/embedding_lookup/53754*+
_output_shapes
:���������d�
Ftoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1IdentityMtoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity:output:0*
T0*+
_output_shapes
:���������d�
"token_and_position_embedding_2/addAddV2Otoken_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1:output:0Otoken_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1:output:0*
T0*+
_output_shapes
:���������d�
Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpVtransformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
>transformer_block_2/multi_head_attention_2/query/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Utransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOpReadVariableOpLtransformer_block_2_multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
4transformer_block_2/multi_head_attention_2/query/addAddV2Gtransformer_block_2/multi_head_attention_2/query/einsum/Einsum:output:0Ktransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOpTtransformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
<transformer_block_2/multi_head_attention_2/key/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Stransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOpReadVariableOpJtransformer_block_2_multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
2transformer_block_2/multi_head_attention_2/key/addAddV2Etransformer_block_2/multi_head_attention_2/key/einsum/Einsum:output:0Itransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpVtransformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
>transformer_block_2/multi_head_attention_2/value/einsum/EinsumEinsum&token_and_position_embedding_2/add:z:0Utransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOpReadVariableOpLtransformer_block_2_multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
4transformer_block_2/multi_head_attention_2/value/addAddV2Gtransformer_block_2/multi_head_attention_2/value/einsum/Einsum:output:0Ktransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������du
0transformer_block_2/multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
.transformer_block_2/multi_head_attention_2/MulMul8transformer_block_2/multi_head_attention_2/query/add:z:09transformer_block_2/multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
8transformer_block_2/multi_head_attention_2/einsum/EinsumEinsum6transformer_block_2/multi_head_attention_2/key/add:z:02transformer_block_2/multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
:transformer_block_2/multi_head_attention_2/softmax/SoftmaxSoftmaxAtransformer_block_2/multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
;transformer_block_2/multi_head_attention_2/dropout/IdentityIdentityDtransformer_block_2/multi_head_attention_2/softmax/Softmax:softmax:0*
T0*/
_output_shapes
:���������dd�
:transformer_block_2/multi_head_attention_2/einsum_1/EinsumEinsumDtransformer_block_2/multi_head_attention_2/dropout/Identity:output:08transformer_block_2/multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpatransformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Itransformer_block_2/multi_head_attention_2/attention_output/einsum/EinsumEinsumCtransformer_block_2/multi_head_attention_2/einsum_1/Einsum:output:0`transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpWtransformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
?transformer_block_2/multi_head_attention_2/attention_output/addAddV2Rtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum:output:0Vtransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
&transformer_block_2/dropout_9/IdentityIdentityCtransformer_block_2/multi_head_attention_2/attention_output/add:z:0*
T0*+
_output_shapes
:���������d�
transformer_block_2/addAddV2&token_and_position_embedding_2/add:z:0/transformer_block_2/dropout_9/Identity:output:0*
T0*+
_output_shapes
:���������d�
Htransformer_block_2/layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
6transformer_block_2/layer_normalization_4/moments/meanMeantransformer_block_2/add:z:0Qtransformer_block_2/layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
>transformer_block_2/layer_normalization_4/moments/StopGradientStopGradient?transformer_block_2/layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Ctransformer_block_2/layer_normalization_4/moments/SquaredDifferenceSquaredDifferencetransformer_block_2/add:z:0Gtransformer_block_2/layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Ltransformer_block_2/layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
:transformer_block_2/layer_normalization_4/moments/varianceMeanGtransformer_block_2/layer_normalization_4/moments/SquaredDifference:z:0Utransformer_block_2/layer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(~
9transformer_block_2/layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
7transformer_block_2/layer_normalization_4/batchnorm/addAddV2Ctransformer_block_2/layer_normalization_4/moments/variance:output:0Btransformer_block_2/layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/RsqrtRsqrt;transformer_block_2/layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOpOtransformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_4/batchnorm/mulMul=transformer_block_2/layer_normalization_4/batchnorm/Rsqrt:y:0Ntransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/mul_1Multransformer_block_2/add:z:0;transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/mul_2Mul?transformer_block_2/layer_normalization_4/moments/mean:output:0;transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpReadVariableOpKtransformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_4/batchnorm/subSubJtransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp:value:0=transformer_block_2/layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_4/batchnorm/add_1AddV2=transformer_block_2/layer_normalization_4/batchnorm/mul_1:z:0;transformer_block_2/layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOpJtransformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
7transformer_block_2/sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
7transformer_block_2/sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
8transformer_block_2/sequential_2/dense_8/Tensordot/ShapeShape=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:�
@transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2GatherV2Atransformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Btransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
=transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1GatherV2Atransformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Ktransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
7transformer_block_2/sequential_2/dense_8/Tensordot/ProdProdDtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Atransformer_block_2/sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: �
:transformer_block_2/sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
9transformer_block_2/sequential_2/dense_8/Tensordot/Prod_1ProdFtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1:output:0Ctransformer_block_2/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
>transformer_block_2/sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
9transformer_block_2/sequential_2/dense_8/Tensordot/concatConcatV2@transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0@transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Gtransformer_block_2/sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_8/Tensordot/stackPack@transformer_block_2/sequential_2/dense_8/Tensordot/Prod:output:0Btransformer_block_2/sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
<transformer_block_2/sequential_2/dense_8/Tensordot/transpose	Transpose=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0Btransformer_block_2/sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
:transformer_block_2/sequential_2/dense_8/Tensordot/ReshapeReshape@transformer_block_2/sequential_2/dense_8/Tensordot/transpose:y:0Atransformer_block_2/sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
9transformer_block_2/sequential_2/dense_8/Tensordot/MatMulMatMulCtransformer_block_2/sequential_2/dense_8/Tensordot/Reshape:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
:transformer_block_2/sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
@transformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_8/Tensordot/concat_1ConcatV2Dtransformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Ctransformer_block_2/sequential_2/dense_8/Tensordot/Const_2:output:0Itransformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
2transformer_block_2/sequential_2/dense_8/TensordotReshapeCtransformer_block_2/sequential_2/dense_8/Tensordot/MatMul:product:0Dtransformer_block_2/sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOpHtransformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
0transformer_block_2/sequential_2/dense_8/BiasAddBiasAdd;transformer_block_2/sequential_2/dense_8/Tensordot:output:0Gtransformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
-transformer_block_2/sequential_2/dense_8/ReluRelu9transformer_block_2/sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOpJtransformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
7transformer_block_2/sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
7transformer_block_2/sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
8transformer_block_2/sequential_2/dense_9/Tensordot/ShapeShape;transformer_block_2/sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:�
@transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2GatherV2Atransformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Btransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
=transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1GatherV2Atransformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Ktransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
7transformer_block_2/sequential_2/dense_9/Tensordot/ProdProdDtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Atransformer_block_2/sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: �
:transformer_block_2/sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
9transformer_block_2/sequential_2/dense_9/Tensordot/Prod_1ProdFtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1:output:0Ctransformer_block_2/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
>transformer_block_2/sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
9transformer_block_2/sequential_2/dense_9/Tensordot/concatConcatV2@transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0@transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Gtransformer_block_2/sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
8transformer_block_2/sequential_2/dense_9/Tensordot/stackPack@transformer_block_2/sequential_2/dense_9/Tensordot/Prod:output:0Btransformer_block_2/sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
<transformer_block_2/sequential_2/dense_9/Tensordot/transpose	Transpose;transformer_block_2/sequential_2/dense_8/Relu:activations:0Btransformer_block_2/sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
:transformer_block_2/sequential_2/dense_9/Tensordot/ReshapeReshape@transformer_block_2/sequential_2/dense_9/Tensordot/transpose:y:0Atransformer_block_2/sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
9transformer_block_2/sequential_2/dense_9/Tensordot/MatMulMatMulCtransformer_block_2/sequential_2/dense_9/Tensordot/Reshape:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
:transformer_block_2/sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
@transformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
;transformer_block_2/sequential_2/dense_9/Tensordot/concat_1ConcatV2Dtransformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Ctransformer_block_2/sequential_2/dense_9/Tensordot/Const_2:output:0Itransformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
2transformer_block_2/sequential_2/dense_9/TensordotReshapeCtransformer_block_2/sequential_2/dense_9/Tensordot/MatMul:product:0Dtransformer_block_2/sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOpHtransformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
0transformer_block_2/sequential_2/dense_9/BiasAddBiasAdd;transformer_block_2/sequential_2/dense_9/Tensordot:output:0Gtransformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
'transformer_block_2/dropout_10/IdentityIdentity9transformer_block_2/sequential_2/dense_9/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
transformer_block_2/add_1AddV2=transformer_block_2/layer_normalization_4/batchnorm/add_1:z:00transformer_block_2/dropout_10/Identity:output:0*
T0*+
_output_shapes
:���������d�
Htransformer_block_2/layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
6transformer_block_2/layer_normalization_5/moments/meanMeantransformer_block_2/add_1:z:0Qtransformer_block_2/layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
>transformer_block_2/layer_normalization_5/moments/StopGradientStopGradient?transformer_block_2/layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Ctransformer_block_2/layer_normalization_5/moments/SquaredDifferenceSquaredDifferencetransformer_block_2/add_1:z:0Gtransformer_block_2/layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Ltransformer_block_2/layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
:transformer_block_2/layer_normalization_5/moments/varianceMeanGtransformer_block_2/layer_normalization_5/moments/SquaredDifference:z:0Utransformer_block_2/layer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(~
9transformer_block_2/layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
7transformer_block_2/layer_normalization_5/batchnorm/addAddV2Ctransformer_block_2/layer_normalization_5/moments/variance:output:0Btransformer_block_2/layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/RsqrtRsqrt;transformer_block_2/layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOpOtransformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_5/batchnorm/mulMul=transformer_block_2/layer_normalization_5/batchnorm/Rsqrt:y:0Ntransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/mul_1Multransformer_block_2/add_1:z:0;transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/mul_2Mul?transformer_block_2/layer_normalization_5/moments/mean:output:0;transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpReadVariableOpKtransformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
7transformer_block_2/layer_normalization_5/batchnorm/subSubJtransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp:value:0=transformer_block_2/layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
9transformer_block_2/layer_normalization_5/batchnorm/add_1AddV2=transformer_block_2/layer_normalization_5/batchnorm/mul_1:z:0;transformer_block_2/layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������ds
1global_average_pooling1d_2/Mean/reduction_indicesConst*
_output_shapes
: *
dtype0*
value	B :�
global_average_pooling1d_2/MeanMean=transformer_block_2/layer_normalization_5/batchnorm/add_1:z:0:global_average_pooling1d_2/Mean/reduction_indices:output:0*
T0*'
_output_shapes
:���������{
dropout_11/IdentityIdentity(global_average_pooling1d_2/Mean:output:0*
T0*'
_output_shapes
:����������
dense_10/MatMul/ReadVariableOpReadVariableOp'dense_10_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
dense_10/MatMulMatMuldropout_11/Identity:output:0&dense_10/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
dense_10/BiasAdd/ReadVariableOpReadVariableOp(dense_10_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_10/BiasAddBiasAdddense_10/MatMul:product:0'dense_10/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������b
dense_10/ReluReludense_10/BiasAdd:output:0*
T0*'
_output_shapes
:���������n
dropout_12/IdentityIdentitydense_10/Relu:activations:0*
T0*'
_output_shapes
:����������
dense_11/MatMul/ReadVariableOpReadVariableOp'dense_11_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
dense_11/MatMulMatMuldropout_12/Identity:output:0&dense_11/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
dense_11/BiasAdd/ReadVariableOpReadVariableOp(dense_11_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_11/BiasAddBiasAdddense_11/MatMul:product:0'dense_11/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������h
dense_11/SoftmaxSoftmaxdense_11/BiasAdd:output:0*
T0*'
_output_shapes
:���������i
IdentityIdentitydense_11/Softmax:softmax:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp ^dense_10/BiasAdd/ReadVariableOp^dense_10/MatMul/ReadVariableOp ^dense_11/BiasAdd/ReadVariableOp^dense_11/MatMul/ReadVariableOp<^token_and_position_embedding_2/embedding_4/embedding_lookup<^token_and_position_embedding_2/embedding_5/embedding_lookupC^transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpG^transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpC^transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpG^transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpO^transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpY^transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpB^transformer_block_2/multi_head_attention_2/key/add/ReadVariableOpL^transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpD^transformer_block_2/multi_head_attention_2/query/add/ReadVariableOpN^transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpD^transformer_block_2/multi_head_attention_2/value/add/ReadVariableOpN^transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp@^transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpB^transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp@^transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpB^transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2B
dense_10/BiasAdd/ReadVariableOpdense_10/BiasAdd/ReadVariableOp2@
dense_10/MatMul/ReadVariableOpdense_10/MatMul/ReadVariableOp2B
dense_11/BiasAdd/ReadVariableOpdense_11/BiasAdd/ReadVariableOp2@
dense_11/MatMul/ReadVariableOpdense_11/MatMul/ReadVariableOp2z
;token_and_position_embedding_2/embedding_4/embedding_lookup;token_and_position_embedding_2/embedding_4/embedding_lookup2z
;token_and_position_embedding_2/embedding_5/embedding_lookup;token_and_position_embedding_2/embedding_5/embedding_lookup2�
Btransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpBtransformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp2�
Ftransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpFtransformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp2�
Btransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpBtransformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp2�
Ftransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpFtransformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp2�
Ntransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpNtransformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp2�
Xtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpXtransformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2�
Atransformer_block_2/multi_head_attention_2/key/add/ReadVariableOpAtransformer_block_2/multi_head_attention_2/key/add/ReadVariableOp2�
Ktransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpKtransformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2�
Ctransformer_block_2/multi_head_attention_2/query/add/ReadVariableOpCtransformer_block_2/multi_head_attention_2/query/add/ReadVariableOp2�
Mtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpMtransformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2�
Ctransformer_block_2/multi_head_attention_2/value/add/ReadVariableOpCtransformer_block_2/multi_head_attention_2/value/add/ReadVariableOp2�
Mtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpMtransformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2�
?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp?transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp2�
Atransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpAtransformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp2�
?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp?transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp2�
Atransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpAtransformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:O K
'
_output_shapes
:���������d
 
_user_specified_nameinputs
�
F
*__inference_dropout_12_layer_call_fn_54531

inputs
identity�
PartitionedCallPartitionedCallinputs*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_52912`
IdentityIdentityPartitionedCall:output:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�

�
C__inference_dense_10_layer_call_and_return_conditional_losses_54526

inputs0
matmul_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�MatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������P
ReluReluBiasAdd:output:0*
T0*'
_output_shapes
:���������a
IdentityIdentityRelu:activations:0^NoOp*
T0*'
_output_shapes
:���������w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�-
�

B__inference_model_2_layer_call_and_return_conditional_losses_53582
input_36
$token_and_position_embedding_2_53530:d7
$token_and_position_embedding_2_53532:	�/
transformer_block_2_53535:+
transformer_block_2_53537:/
transformer_block_2_53539:+
transformer_block_2_53541:/
transformer_block_2_53543:+
transformer_block_2_53545:/
transformer_block_2_53547:'
transformer_block_2_53549:'
transformer_block_2_53551:'
transformer_block_2_53553:+
transformer_block_2_53555:'
transformer_block_2_53557:+
transformer_block_2_53559:'
transformer_block_2_53561:'
transformer_block_2_53563:'
transformer_block_2_53565: 
dense_10_53570:
dense_10_53572: 
dense_11_53576:
dense_11_53578:
identity�� dense_10/StatefulPartitionedCall� dense_11/StatefulPartitionedCall�"dropout_11/StatefulPartitionedCall�"dropout_12/StatefulPartitionedCall�6token_and_position_embedding_2/StatefulPartitionedCall�+transformer_block_2/StatefulPartitionedCall�
6token_and_position_embedding_2/StatefulPartitionedCallStatefulPartitionedCallinput_3$token_and_position_embedding_2_53530$token_and_position_embedding_2_53532*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *b
f]R[
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715�
+transformer_block_2/StatefulPartitionedCallStatefulPartitionedCall?token_and_position_embedding_2/StatefulPartitionedCall:output:0transformer_block_2_53535transformer_block_2_53537transformer_block_2_53539transformer_block_2_53541transformer_block_2_53543transformer_block_2_53545transformer_block_2_53547transformer_block_2_53549transformer_block_2_53551transformer_block_2_53553transformer_block_2_53555transformer_block_2_53557transformer_block_2_53559transformer_block_2_53561transformer_block_2_53563transformer_block_2_53565*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_53225�
*global_average_pooling1d_2/PartitionedCallPartitionedCall4transformer_block_2/StatefulPartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *^
fYRW
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681�
"dropout_11/StatefulPartitionedCallStatefulPartitionedCall3global_average_pooling1d_2/PartitionedCall:output:0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_11_layer_call_and_return_conditional_losses_53042�
 dense_10/StatefulPartitionedCallStatefulPartitionedCall+dropout_11/StatefulPartitionedCall:output:0dense_10_53570dense_10_53572*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_10_layer_call_and_return_conditional_losses_52901�
"dropout_12/StatefulPartitionedCallStatefulPartitionedCall)dense_10/StatefulPartitionedCall:output:0#^dropout_11/StatefulPartitionedCall*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_53009�
 dense_11/StatefulPartitionedCallStatefulPartitionedCall+dropout_12/StatefulPartitionedCall:output:0dense_11_53576dense_11_53578*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_11_layer_call_and_return_conditional_losses_52925x
IdentityIdentity)dense_11/StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp!^dense_10/StatefulPartitionedCall!^dense_11/StatefulPartitionedCall#^dropout_11/StatefulPartitionedCall#^dropout_12/StatefulPartitionedCall7^token_and_position_embedding_2/StatefulPartitionedCall,^transformer_block_2/StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2D
 dense_10/StatefulPartitionedCall dense_10/StatefulPartitionedCall2D
 dense_11/StatefulPartitionedCall dense_11/StatefulPartitionedCall2H
"dropout_11/StatefulPartitionedCall"dropout_11/StatefulPartitionedCall2H
"dropout_12/StatefulPartitionedCall"dropout_12/StatefulPartitionedCall2p
6token_and_position_embedding_2/StatefulPartitionedCall6token_and_position_embedding_2/StatefulPartitionedCall2Z
+transformer_block_2/StatefulPartitionedCall+transformer_block_2/StatefulPartitionedCall:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
�
�
#__inference_signature_wrapper_53639
input_3
unknown:d
	unknown_0:	�
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:

unknown_15:

unknown_16:

unknown_17:

unknown_18:

unknown_19:

unknown_20:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinput_3unknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14
unknown_15
unknown_16
unknown_17
unknown_18
unknown_19
unknown_20*"
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*8
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *)
f$R"
 __inference__wrapped_model_52478o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
�
c
E__inference_dropout_12_layer_call_and_return_conditional_losses_54541

inputs

identity_1N
IdentityIdentityinputs*
T0*'
_output_shapes
:���������[

Identity_1IdentityIdentity:output:0*
T0*'
_output_shapes
:���������"!

identity_1Identity_1:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
'__inference_dense_8_layer_call_fn_54722

inputs
unknown:
	unknown_0:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *K
fFRD
B__inference_dense_8_layer_call_and_return_conditional_losses_52516s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
,__inference_sequential_2_layer_call_fn_54599

inputs
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2*
Tin	
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*&
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *P
fKRI
G__inference_sequential_2_layer_call_and_return_conditional_losses_52619s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
,__inference_sequential_2_layer_call_fn_54586

inputs
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2*
Tin	
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*&
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *P
fKRI
G__inference_sequential_2_layer_call_and_return_conditional_losses_52559s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
c
*__inference_dropout_12_layer_call_fn_54536

inputs
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputs*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������* 
_read_only_resource_inputs
 *-
config_proto

CPU

GPU 2J 8� *N
fIRG
E__inference_dropout_12_layer_call_and_return_conditional_losses_53009o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�	
d
E__inference_dropout_11_layer_call_and_return_conditional_losses_53042

inputs
identity�R
dropout/ConstConst*
_output_shapes
: *
dtype0*
valueB
 *�8�?d
dropout/MulMulinputsdropout/Const:output:0*
T0*'
_output_shapes
:���������C
dropout/ShapeShapeinputs*
T0*
_output_shapes
:�
$dropout/random_uniform/RandomUniformRandomUniformdropout/Shape:output:0*
T0*'
_output_shapes
:���������*
dtype0[
dropout/GreaterEqual/yConst*
_output_shapes
: *
dtype0*
valueB
 *���=�
dropout/GreaterEqualGreaterEqual-dropout/random_uniform/RandomUniform:output:0dropout/GreaterEqual/y:output:0*
T0*'
_output_shapes
:���������o
dropout/CastCastdropout/GreaterEqual:z:0*

DstT0*

SrcT0
*'
_output_shapes
:���������i
dropout/Mul_1Muldropout/Mul:z:0dropout/Cast:y:0*
T0*'
_output_shapes
:���������Y
IdentityIdentitydropout/Mul_1:z:0*
T0*'
_output_shapes
:���������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
��
�
 __inference__wrapped_model_52478
input_3[
Imodel_2_token_and_position_embedding_2_embedding_5_embedding_lookup_52324:d\
Imodel_2_token_and_position_embedding_2_embedding_4_embedding_lookup_52330:	�t
^model_2_transformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource:f
Tmodel_2_transformer_block_2_multi_head_attention_2_query_add_readvariableop_resource:r
\model_2_transformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource:d
Rmodel_2_transformer_block_2_multi_head_attention_2_key_add_readvariableop_resource:t
^model_2_transformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource:f
Tmodel_2_transformer_block_2_multi_head_attention_2_value_add_readvariableop_resource:
imodel_2_transformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:m
_model_2_transformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource:e
Wmodel_2_transformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource:a
Smodel_2_transformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource:d
Rmodel_2_transformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource:^
Pmodel_2_transformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource:d
Rmodel_2_transformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource:^
Pmodel_2_transformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource:e
Wmodel_2_transformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource:a
Smodel_2_transformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource:A
/model_2_dense_10_matmul_readvariableop_resource:>
0model_2_dense_10_biasadd_readvariableop_resource:A
/model_2_dense_11_matmul_readvariableop_resource:>
0model_2_dense_11_biasadd_readvariableop_resource:
identity��'model_2/dense_10/BiasAdd/ReadVariableOp�&model_2/dense_10/MatMul/ReadVariableOp�'model_2/dense_11/BiasAdd/ReadVariableOp�&model_2/dense_11/MatMul/ReadVariableOp�Cmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup�Cmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup�Jmodel_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp�Nmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp�Jmodel_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp�Nmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp�Vmodel_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp�`model_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�Imodel_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOp�Smodel_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�Kmodel_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOp�Umodel_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�Kmodel_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOp�Umodel_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�Gmodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp�Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp�Gmodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp�Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpc
,model_2/token_and_position_embedding_2/ShapeShapeinput_3*
T0*
_output_shapes
:�
:model_2/token_and_position_embedding_2/strided_slice/stackConst*
_output_shapes
:*
dtype0*
valueB:
����������
<model_2/token_and_position_embedding_2/strided_slice/stack_1Const*
_output_shapes
:*
dtype0*
valueB: �
<model_2/token_and_position_embedding_2/strided_slice/stack_2Const*
_output_shapes
:*
dtype0*
valueB:�
4model_2/token_and_position_embedding_2/strided_sliceStridedSlice5model_2/token_and_position_embedding_2/Shape:output:0Cmodel_2/token_and_position_embedding_2/strided_slice/stack:output:0Emodel_2/token_and_position_embedding_2/strided_slice/stack_1:output:0Emodel_2/token_and_position_embedding_2/strided_slice/stack_2:output:0*
Index0*
T0*
_output_shapes
: *
shrink_axis_maskt
2model_2/token_and_position_embedding_2/range/startConst*
_output_shapes
: *
dtype0*
value	B : t
2model_2/token_and_position_embedding_2/range/deltaConst*
_output_shapes
: *
dtype0*
value	B :�
,model_2/token_and_position_embedding_2/rangeRange;model_2/token_and_position_embedding_2/range/start:output:0=model_2/token_and_position_embedding_2/strided_slice:output:0;model_2/token_and_position_embedding_2/range/delta:output:0*
_output_shapes
:d�
Cmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookupResourceGatherImodel_2_token_and_position_embedding_2_embedding_5_embedding_lookup_523245model_2/token_and_position_embedding_2/range:output:0*
Tindices0*\
_classR
PNloc:@model_2/token_and_position_embedding_2/embedding_5/embedding_lookup/52324*
_output_shapes

:d*
dtype0�
Lmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup/IdentityIdentityLmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup:output:0*
T0*\
_classR
PNloc:@model_2/token_and_position_embedding_2/embedding_5/embedding_lookup/52324*
_output_shapes

:d�
Nmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1IdentityUmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup/Identity:output:0*
T0*
_output_shapes

:d�
7model_2/token_and_position_embedding_2/embedding_4/CastCastinput_3*

DstT0*

SrcT0*'
_output_shapes
:���������d�
Cmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookupResourceGatherImodel_2_token_and_position_embedding_2_embedding_4_embedding_lookup_52330;model_2/token_and_position_embedding_2/embedding_4/Cast:y:0*
Tindices0*\
_classR
PNloc:@model_2/token_and_position_embedding_2/embedding_4/embedding_lookup/52330*+
_output_shapes
:���������d*
dtype0�
Lmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup/IdentityIdentityLmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup:output:0*
T0*\
_classR
PNloc:@model_2/token_and_position_embedding_2/embedding_4/embedding_lookup/52330*+
_output_shapes
:���������d�
Nmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1IdentityUmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup/Identity:output:0*
T0*+
_output_shapes
:���������d�
*model_2/token_and_position_embedding_2/addAddV2Wmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup/Identity_1:output:0Wmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup/Identity_1:output:0*
T0*+
_output_shapes
:���������d�
Umodel_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOp^model_2_transformer_block_2_multi_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Fmodel_2/transformer_block_2/multi_head_attention_2/query/einsum/EinsumEinsum.model_2/token_and_position_embedding_2/add:z:0]model_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Kmodel_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOpReadVariableOpTmodel_2_transformer_block_2_multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
<model_2/transformer_block_2/multi_head_attention_2/query/addAddV2Omodel_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum:output:0Smodel_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Smodel_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOp\model_2_transformer_block_2_multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Dmodel_2/transformer_block_2/multi_head_attention_2/key/einsum/EinsumEinsum.model_2/token_and_position_embedding_2/add:z:0[model_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Imodel_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOpReadVariableOpRmodel_2_transformer_block_2_multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
:model_2/transformer_block_2/multi_head_attention_2/key/addAddV2Mmodel_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum:output:0Qmodel_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
Umodel_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOp^model_2_transformer_block_2_multi_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Fmodel_2/transformer_block_2/multi_head_attention_2/value/einsum/EinsumEinsum.model_2/token_and_position_embedding_2/add:z:0]model_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
Kmodel_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOpReadVariableOpTmodel_2_transformer_block_2_multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
<model_2/transformer_block_2/multi_head_attention_2/value/addAddV2Omodel_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum:output:0Smodel_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d}
8model_2/transformer_block_2/multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
6model_2/transformer_block_2/multi_head_attention_2/MulMul@model_2/transformer_block_2/multi_head_attention_2/query/add:z:0Amodel_2/transformer_block_2/multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
@model_2/transformer_block_2/multi_head_attention_2/einsum/EinsumEinsum>model_2/transformer_block_2/multi_head_attention_2/key/add:z:0:model_2/transformer_block_2/multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
Bmodel_2/transformer_block_2/multi_head_attention_2/softmax/SoftmaxSoftmaxImodel_2/transformer_block_2/multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
Cmodel_2/transformer_block_2/multi_head_attention_2/dropout/IdentityIdentityLmodel_2/transformer_block_2/multi_head_attention_2/softmax/Softmax:softmax:0*
T0*/
_output_shapes
:���������dd�
Bmodel_2/transformer_block_2/multi_head_attention_2/einsum_1/EinsumEinsumLmodel_2/transformer_block_2/multi_head_attention_2/dropout/Identity:output:0@model_2/transformer_block_2/multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
`model_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpimodel_2_transformer_block_2_multi_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
Qmodel_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/EinsumEinsumKmodel_2/transformer_block_2/multi_head_attention_2/einsum_1/Einsum:output:0hmodel_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
Vmodel_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOp_model_2_transformer_block_2_multi_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
Gmodel_2/transformer_block_2/multi_head_attention_2/attention_output/addAddV2Zmodel_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum:output:0^model_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
.model_2/transformer_block_2/dropout_9/IdentityIdentityKmodel_2/transformer_block_2/multi_head_attention_2/attention_output/add:z:0*
T0*+
_output_shapes
:���������d�
model_2/transformer_block_2/addAddV2.model_2/token_and_position_embedding_2/add:z:07model_2/transformer_block_2/dropout_9/Identity:output:0*
T0*+
_output_shapes
:���������d�
Pmodel_2/transformer_block_2/layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
>model_2/transformer_block_2/layer_normalization_4/moments/meanMean#model_2/transformer_block_2/add:z:0Ymodel_2/transformer_block_2/layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
Fmodel_2/transformer_block_2/layer_normalization_4/moments/StopGradientStopGradientGmodel_2/transformer_block_2/layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Kmodel_2/transformer_block_2/layer_normalization_4/moments/SquaredDifferenceSquaredDifference#model_2/transformer_block_2/add:z:0Omodel_2/transformer_block_2/layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Tmodel_2/transformer_block_2/layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
Bmodel_2/transformer_block_2/layer_normalization_4/moments/varianceMeanOmodel_2/transformer_block_2/layer_normalization_4/moments/SquaredDifference:z:0]model_2/transformer_block_2/layer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
Amodel_2/transformer_block_2/layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
?model_2/transformer_block_2/layer_normalization_4/batchnorm/addAddV2Kmodel_2/transformer_block_2/layer_normalization_4/moments/variance:output:0Jmodel_2/transformer_block_2/layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_4/batchnorm/RsqrtRsqrtCmodel_2/transformer_block_2/layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Nmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOpWmodel_2_transformer_block_2_layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
?model_2/transformer_block_2/layer_normalization_4/batchnorm/mulMulEmodel_2/transformer_block_2/layer_normalization_4/batchnorm/Rsqrt:y:0Vmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul_1Mul#model_2/transformer_block_2/add:z:0Cmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul_2MulGmodel_2/transformer_block_2/layer_normalization_4/moments/mean:output:0Cmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Jmodel_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpReadVariableOpSmodel_2_transformer_block_2_layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
?model_2/transformer_block_2/layer_normalization_4/batchnorm/subSubRmodel_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp:value:0Emodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_4/batchnorm/add_1AddV2Emodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul_1:z:0Cmodel_2/transformer_block_2/layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOpRmodel_2_transformer_block_2_sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
?model_2/transformer_block_2/sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
?model_2/transformer_block_2/sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
@model_2/transformer_block_2/sequential_2/dense_8/Tensordot/ShapeShapeEmodel_2/transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:�
Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Cmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2GatherV2Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0Qmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Jmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Emodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1GatherV2Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Shape:output:0Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Smodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
@model_2/transformer_block_2/sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
?model_2/transformer_block_2/sequential_2/dense_8/Tensordot/ProdProdLmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: �
Bmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
Amodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Prod_1ProdNmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2_1:output:0Kmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
Fmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Amodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concatConcatV2Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/free:output:0Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/axes:output:0Omodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
@model_2/transformer_block_2/sequential_2/dense_8/Tensordot/stackPackHmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Prod:output:0Jmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
Dmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/transpose	TransposeEmodel_2/transformer_block_2/layer_normalization_4/batchnorm/add_1:z:0Jmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Bmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReshapeReshapeHmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/transpose:y:0Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Amodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/MatMulMatMulKmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Reshape:output:0Qmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
Bmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
Hmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Cmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat_1ConcatV2Lmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/GatherV2:output:0Kmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/Const_2:output:0Qmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
:model_2/transformer_block_2/sequential_2/dense_8/TensordotReshapeKmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/MatMul:product:0Lmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
Gmodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOpPmodel_2_transformer_block_2_sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
8model_2/transformer_block_2/sequential_2/dense_8/BiasAddBiasAddCmodel_2/transformer_block_2/sequential_2/dense_8/Tensordot:output:0Omodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
5model_2/transformer_block_2/sequential_2/dense_8/ReluReluAmodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOpRmodel_2_transformer_block_2_sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0�
?model_2/transformer_block_2/sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:�
?model_2/transformer_block_2/sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       �
@model_2/transformer_block_2/sequential_2/dense_9/Tensordot/ShapeShapeCmodel_2/transformer_block_2/sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:�
Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Cmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2GatherV2Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0Qmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
Jmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Emodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1GatherV2Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Shape:output:0Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Smodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:�
@model_2/transformer_block_2/sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
?model_2/transformer_block_2/sequential_2/dense_9/Tensordot/ProdProdLmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: �
Bmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
Amodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Prod_1ProdNmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2_1:output:0Kmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: �
Fmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Amodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concatConcatV2Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/free:output:0Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/axes:output:0Omodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
@model_2/transformer_block_2/sequential_2/dense_9/Tensordot/stackPackHmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Prod:output:0Jmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
Dmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/transpose	TransposeCmodel_2/transformer_block_2/sequential_2/dense_8/Relu:activations:0Jmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Bmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReshapeReshapeHmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/transpose:y:0Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Amodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/MatMulMatMulKmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Reshape:output:0Qmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
Bmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:�
Hmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Cmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat_1ConcatV2Lmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/GatherV2:output:0Kmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/Const_2:output:0Qmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
:model_2/transformer_block_2/sequential_2/dense_9/TensordotReshapeKmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/MatMul:product:0Lmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
Gmodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOpPmodel_2_transformer_block_2_sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
8model_2/transformer_block_2/sequential_2/dense_9/BiasAddBiasAddCmodel_2/transformer_block_2/sequential_2/dense_9/Tensordot:output:0Omodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
/model_2/transformer_block_2/dropout_10/IdentityIdentityAmodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
!model_2/transformer_block_2/add_1AddV2Emodel_2/transformer_block_2/layer_normalization_4/batchnorm/add_1:z:08model_2/transformer_block_2/dropout_10/Identity:output:0*
T0*+
_output_shapes
:���������d�
Pmodel_2/transformer_block_2/layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
>model_2/transformer_block_2/layer_normalization_5/moments/meanMean%model_2/transformer_block_2/add_1:z:0Ymodel_2/transformer_block_2/layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
Fmodel_2/transformer_block_2/layer_normalization_5/moments/StopGradientStopGradientGmodel_2/transformer_block_2/layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
Kmodel_2/transformer_block_2/layer_normalization_5/moments/SquaredDifferenceSquaredDifference%model_2/transformer_block_2/add_1:z:0Omodel_2/transformer_block_2/layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
Tmodel_2/transformer_block_2/layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
Bmodel_2/transformer_block_2/layer_normalization_5/moments/varianceMeanOmodel_2/transformer_block_2/layer_normalization_5/moments/SquaredDifference:z:0]model_2/transformer_block_2/layer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
Amodel_2/transformer_block_2/layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
?model_2/transformer_block_2/layer_normalization_5/batchnorm/addAddV2Kmodel_2/transformer_block_2/layer_normalization_5/moments/variance:output:0Jmodel_2/transformer_block_2/layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_5/batchnorm/RsqrtRsqrtCmodel_2/transformer_block_2/layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
Nmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOpWmodel_2_transformer_block_2_layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
?model_2/transformer_block_2/layer_normalization_5/batchnorm/mulMulEmodel_2/transformer_block_2/layer_normalization_5/batchnorm/Rsqrt:y:0Vmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul_1Mul%model_2/transformer_block_2/add_1:z:0Cmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul_2MulGmodel_2/transformer_block_2/layer_normalization_5/moments/mean:output:0Cmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
Jmodel_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpReadVariableOpSmodel_2_transformer_block_2_layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
?model_2/transformer_block_2/layer_normalization_5/batchnorm/subSubRmodel_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp:value:0Emodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
Amodel_2/transformer_block_2/layer_normalization_5/batchnorm/add_1AddV2Emodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul_1:z:0Cmodel_2/transformer_block_2/layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d{
9model_2/global_average_pooling1d_2/Mean/reduction_indicesConst*
_output_shapes
: *
dtype0*
value	B :�
'model_2/global_average_pooling1d_2/MeanMeanEmodel_2/transformer_block_2/layer_normalization_5/batchnorm/add_1:z:0Bmodel_2/global_average_pooling1d_2/Mean/reduction_indices:output:0*
T0*'
_output_shapes
:����������
model_2/dropout_11/IdentityIdentity0model_2/global_average_pooling1d_2/Mean:output:0*
T0*'
_output_shapes
:����������
&model_2/dense_10/MatMul/ReadVariableOpReadVariableOp/model_2_dense_10_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
model_2/dense_10/MatMulMatMul$model_2/dropout_11/Identity:output:0.model_2/dense_10/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
'model_2/dense_10/BiasAdd/ReadVariableOpReadVariableOp0model_2_dense_10_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
model_2/dense_10/BiasAddBiasAdd!model_2/dense_10/MatMul:product:0/model_2/dense_10/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������r
model_2/dense_10/ReluRelu!model_2/dense_10/BiasAdd:output:0*
T0*'
_output_shapes
:���������~
model_2/dropout_12/IdentityIdentity#model_2/dense_10/Relu:activations:0*
T0*'
_output_shapes
:����������
&model_2/dense_11/MatMul/ReadVariableOpReadVariableOp/model_2_dense_11_matmul_readvariableop_resource*
_output_shapes

:*
dtype0�
model_2/dense_11/MatMulMatMul$model_2/dropout_12/Identity:output:0.model_2/dense_11/MatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:����������
'model_2/dense_11/BiasAdd/ReadVariableOpReadVariableOp0model_2_dense_11_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
model_2/dense_11/BiasAddBiasAdd!model_2/dense_11/MatMul:product:0/model_2/dense_11/BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������x
model_2/dense_11/SoftmaxSoftmax!model_2/dense_11/BiasAdd:output:0*
T0*'
_output_shapes
:���������q
IdentityIdentity"model_2/dense_11/Softmax:softmax:0^NoOp*
T0*'
_output_shapes
:����������
NoOpNoOp(^model_2/dense_10/BiasAdd/ReadVariableOp'^model_2/dense_10/MatMul/ReadVariableOp(^model_2/dense_11/BiasAdd/ReadVariableOp'^model_2/dense_11/MatMul/ReadVariableOpD^model_2/token_and_position_embedding_2/embedding_4/embedding_lookupD^model_2/token_and_position_embedding_2/embedding_5/embedding_lookupK^model_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpO^model_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpK^model_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpO^model_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpW^model_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpa^model_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpJ^model_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOpT^model_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpL^model_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOpV^model_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpL^model_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOpV^model_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpH^model_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpJ^model_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpH^model_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpJ^model_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*R
_input_shapesA
?:���������d: : : : : : : : : : : : : : : : : : : : : : 2R
'model_2/dense_10/BiasAdd/ReadVariableOp'model_2/dense_10/BiasAdd/ReadVariableOp2P
&model_2/dense_10/MatMul/ReadVariableOp&model_2/dense_10/MatMul/ReadVariableOp2R
'model_2/dense_11/BiasAdd/ReadVariableOp'model_2/dense_11/BiasAdd/ReadVariableOp2P
&model_2/dense_11/MatMul/ReadVariableOp&model_2/dense_11/MatMul/ReadVariableOp2�
Cmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookupCmodel_2/token_and_position_embedding_2/embedding_4/embedding_lookup2�
Cmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookupCmodel_2/token_and_position_embedding_2/embedding_5/embedding_lookup2�
Jmodel_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOpJmodel_2/transformer_block_2/layer_normalization_4/batchnorm/ReadVariableOp2�
Nmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOpNmodel_2/transformer_block_2/layer_normalization_4/batchnorm/mul/ReadVariableOp2�
Jmodel_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOpJmodel_2/transformer_block_2/layer_normalization_5/batchnorm/ReadVariableOp2�
Nmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOpNmodel_2/transformer_block_2/layer_normalization_5/batchnorm/mul/ReadVariableOp2�
Vmodel_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOpVmodel_2/transformer_block_2/multi_head_attention_2/attention_output/add/ReadVariableOp2�
`model_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp`model_2/transformer_block_2/multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2�
Imodel_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOpImodel_2/transformer_block_2/multi_head_attention_2/key/add/ReadVariableOp2�
Smodel_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOpSmodel_2/transformer_block_2/multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2�
Kmodel_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOpKmodel_2/transformer_block_2/multi_head_attention_2/query/add/ReadVariableOp2�
Umodel_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOpUmodel_2/transformer_block_2/multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2�
Kmodel_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOpKmodel_2/transformer_block_2/multi_head_attention_2/value/add/ReadVariableOp2�
Umodel_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOpUmodel_2/transformer_block_2/multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2�
Gmodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOpGmodel_2/transformer_block_2/sequential_2/dense_8/BiasAdd/ReadVariableOp2�
Imodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOpImodel_2/transformer_block_2/sequential_2/dense_8/Tensordot/ReadVariableOp2�
Gmodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOpGmodel_2/transformer_block_2/sequential_2/dense_9/BiasAdd/ReadVariableOp2�
Imodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOpImodel_2/transformer_block_2/sequential_2/dense_9/Tensordot/ReadVariableOp:P L
'
_output_shapes
:���������d
!
_user_specified_name	input_3
�
q
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_52681

inputs
identityX
Mean/reduction_indicesConst*
_output_shapes
: *
dtype0*
value	B :p
MeanMeaninputsMean/reduction_indices:output:0*
T0*0
_output_shapes
:������������������^
IdentityIdentityMean:output:0*
T0*0
_output_shapes
:������������������"
identityIdentity:output:0*(
_construction_contextkEagerRuntime*<
_input_shapes+
):'���������������������������:e a
=
_output_shapes+
):'���������������������������
 
_user_specified_nameinputs
�
�
B__inference_dense_9_layer_call_and_return_conditional_losses_54792

inputs3
!tensordot_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�Tensordot/ReadVariableOpz
Tensordot/ReadVariableOpReadVariableOp!tensordot_readvariableop_resource*
_output_shapes

:*
dtype0X
Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:_
Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       E
Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:Y
Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2GatherV2Tensordot/Shape:output:0Tensordot/free:output:0 Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:[
Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2_1GatherV2Tensordot/Shape:output:0Tensordot/axes:output:0"Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:Y
Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: n
Tensordot/ProdProdTensordot/GatherV2:output:0Tensordot/Const:output:0*
T0*
_output_shapes
: [
Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: t
Tensordot/Prod_1ProdTensordot/GatherV2_1:output:0Tensordot/Const_1:output:0*
T0*
_output_shapes
: W
Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concatConcatV2Tensordot/free:output:0Tensordot/axes:output:0Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:y
Tensordot/stackPackTensordot/Prod:output:0Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:y
Tensordot/transpose	TransposeinputsTensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Tensordot/ReshapeReshapeTensordot/transpose:y:0Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Tensordot/MatMulMatMulTensordot/Reshape:output:0 Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������[
Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:Y
Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concat_1ConcatV2Tensordot/GatherV2:output:0Tensordot/Const_2:output:0 Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
	TensordotReshapeTensordot/MatMul:product:0Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������dr
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0|
BiasAddBiasAddTensordot:output:0BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dc
IdentityIdentityBiasAdd:output:0^NoOp*
T0*+
_output_shapes
:���������dz
NoOpNoOp^BiasAdd/ReadVariableOp^Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp24
Tensordot/ReadVariableOpTensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
3__inference_transformer_block_2_layer_call_fn_54201

inputs
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_53225s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
(__inference_dense_11_layer_call_fn_54562

inputs
unknown:
	unknown_0:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_11_layer_call_and_return_conditional_losses_52925o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_52715
x4
"embedding_5_embedding_lookup_52702:d5
"embedding_4_embedding_lookup_52708:	�
identity��embedding_4/embedding_lookup�embedding_5/embedding_lookup6
ShapeShapex*
T0*
_output_shapes
:f
strided_slice/stackConst*
_output_shapes
:*
dtype0*
valueB:
���������_
strided_slice/stack_1Const*
_output_shapes
:*
dtype0*
valueB: _
strided_slice/stack_2Const*
_output_shapes
:*
dtype0*
valueB:�
strided_sliceStridedSliceShape:output:0strided_slice/stack:output:0strided_slice/stack_1:output:0strided_slice/stack_2:output:0*
Index0*
T0*
_output_shapes
: *
shrink_axis_maskM
range/startConst*
_output_shapes
: *
dtype0*
value	B : M
range/deltaConst*
_output_shapes
: *
dtype0*
value	B :n
rangeRangerange/start:output:0strided_slice:output:0range/delta:output:0*
_output_shapes
:d�
embedding_5/embedding_lookupResourceGather"embedding_5_embedding_lookup_52702range:output:0*
Tindices0*5
_class+
)'loc:@embedding_5/embedding_lookup/52702*
_output_shapes

:d*
dtype0�
%embedding_5/embedding_lookup/IdentityIdentity%embedding_5/embedding_lookup:output:0*
T0*5
_class+
)'loc:@embedding_5/embedding_lookup/52702*
_output_shapes

:d�
'embedding_5/embedding_lookup/Identity_1Identity.embedding_5/embedding_lookup/Identity:output:0*
T0*
_output_shapes

:d\
embedding_4/CastCastx*

DstT0*

SrcT0*'
_output_shapes
:���������d�
embedding_4/embedding_lookupResourceGather"embedding_4_embedding_lookup_52708embedding_4/Cast:y:0*
Tindices0*5
_class+
)'loc:@embedding_4/embedding_lookup/52708*+
_output_shapes
:���������d*
dtype0�
%embedding_4/embedding_lookup/IdentityIdentity%embedding_4/embedding_lookup:output:0*
T0*5
_class+
)'loc:@embedding_4/embedding_lookup/52708*+
_output_shapes
:���������d�
'embedding_4/embedding_lookup/Identity_1Identity.embedding_4/embedding_lookup/Identity:output:0*
T0*+
_output_shapes
:���������d�
addAddV20embedding_4/embedding_lookup/Identity_1:output:00embedding_5/embedding_lookup/Identity_1:output:0*
T0*+
_output_shapes
:���������dZ
IdentityIdentityadd:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp^embedding_4/embedding_lookup^embedding_5/embedding_lookup*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������d: : 2<
embedding_4/embedding_lookupembedding_4/embedding_lookup2<
embedding_5/embedding_lookupembedding_5/embedding_lookup:J F
'
_output_shapes
:���������d

_user_specified_namex
�

�
C__inference_dense_11_layer_call_and_return_conditional_losses_54573

inputs0
matmul_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�MatMul/ReadVariableOpt
MatMul/ReadVariableOpReadVariableOpmatmul_readvariableop_resource*
_output_shapes

:*
dtype0i
MatMulMatMulinputsMatMul/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������r
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0v
BiasAddBiasAddMatMul:product:0BiasAdd/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������V
SoftmaxSoftmaxBiasAdd:output:0*
T0*'
_output_shapes
:���������`
IdentityIdentitySoftmax:softmax:0^NoOp*
T0*'
_output_shapes
:���������w
NoOpNoOp^BiasAdd/ReadVariableOp^MatMul/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp2.
MatMul/ReadVariableOpMatMul/ReadVariableOp:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
B__inference_dense_8_layer_call_and_return_conditional_losses_54753

inputs3
!tensordot_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�Tensordot/ReadVariableOpz
Tensordot/ReadVariableOpReadVariableOp!tensordot_readvariableop_resource*
_output_shapes

:*
dtype0X
Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:_
Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       E
Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:Y
Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2GatherV2Tensordot/Shape:output:0Tensordot/free:output:0 Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:[
Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2_1GatherV2Tensordot/Shape:output:0Tensordot/axes:output:0"Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:Y
Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: n
Tensordot/ProdProdTensordot/GatherV2:output:0Tensordot/Const:output:0*
T0*
_output_shapes
: [
Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: t
Tensordot/Prod_1ProdTensordot/GatherV2_1:output:0Tensordot/Const_1:output:0*
T0*
_output_shapes
: W
Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concatConcatV2Tensordot/free:output:0Tensordot/axes:output:0Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:y
Tensordot/stackPackTensordot/Prod:output:0Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:y
Tensordot/transpose	TransposeinputsTensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Tensordot/ReshapeReshapeTensordot/transpose:y:0Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Tensordot/MatMulMatMulTensordot/Reshape:output:0 Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������[
Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:Y
Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concat_1ConcatV2Tensordot/GatherV2:output:0Tensordot/Const_2:output:0 Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
	TensordotReshapeTensordot/MatMul:product:0Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������dr
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0|
BiasAddBiasAddTensordot:output:0BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dT
ReluReluBiasAdd:output:0*
T0*+
_output_shapes
:���������de
IdentityIdentityRelu:activations:0^NoOp*
T0*+
_output_shapes
:���������dz
NoOpNoOp^BiasAdd/ReadVariableOp^Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp24
Tensordot/ReadVariableOpTensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
��
�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_52848

inputsX
Bmulti_head_attention_2_query_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_query_add_readvariableop_resource:V
@multi_head_attention_2_key_einsum_einsum_readvariableop_resource:H
6multi_head_attention_2_key_add_readvariableop_resource:X
Bmulti_head_attention_2_value_einsum_einsum_readvariableop_resource:J
8multi_head_attention_2_value_add_readvariableop_resource:c
Mmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource:Q
Cmulti_head_attention_2_attention_output_add_readvariableop_resource:I
;layer_normalization_4_batchnorm_mul_readvariableop_resource:E
7layer_normalization_4_batchnorm_readvariableop_resource:H
6sequential_2_dense_8_tensordot_readvariableop_resource:B
4sequential_2_dense_8_biasadd_readvariableop_resource:H
6sequential_2_dense_9_tensordot_readvariableop_resource:B
4sequential_2_dense_9_biasadd_readvariableop_resource:I
;layer_normalization_5_batchnorm_mul_readvariableop_resource:E
7layer_normalization_5_batchnorm_readvariableop_resource:
identity��.layer_normalization_4/batchnorm/ReadVariableOp�2layer_normalization_4/batchnorm/mul/ReadVariableOp�.layer_normalization_5/batchnorm/ReadVariableOp�2layer_normalization_5/batchnorm/mul/ReadVariableOp�:multi_head_attention_2/attention_output/add/ReadVariableOp�Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp�-multi_head_attention_2/key/add/ReadVariableOp�7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/query/add/ReadVariableOp�9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp�/multi_head_attention_2/value/add/ReadVariableOp�9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp�+sequential_2/dense_8/BiasAdd/ReadVariableOp�-sequential_2/dense_8/Tensordot/ReadVariableOp�+sequential_2/dense_9/BiasAdd/ReadVariableOp�-sequential_2/dense_9/Tensordot/ReadVariableOp�
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_query_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/query/einsum/EinsumEinsuminputsAmulti_head_attention_2/query/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/query/add/ReadVariableOpReadVariableOp8multi_head_attention_2_query_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/query/addAddV23multi_head_attention_2/query/einsum/Einsum:output:07multi_head_attention_2/query/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOpReadVariableOp@multi_head_attention_2_key_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
(multi_head_attention_2/key/einsum/EinsumEinsuminputs?multi_head_attention_2/key/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
-multi_head_attention_2/key/add/ReadVariableOpReadVariableOp6multi_head_attention_2_key_add_readvariableop_resource*
_output_shapes

:*
dtype0�
multi_head_attention_2/key/addAddV21multi_head_attention_2/key/einsum/Einsum:output:05multi_head_attention_2/key/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������d�
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOpReadVariableOpBmulti_head_attention_2_value_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
*multi_head_attention_2/value/einsum/EinsumEinsuminputsAmulti_head_attention_2/value/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*/
_output_shapes
:���������d*
equationabc,cde->abde�
/multi_head_attention_2/value/add/ReadVariableOpReadVariableOp8multi_head_attention_2_value_add_readvariableop_resource*
_output_shapes

:*
dtype0�
 multi_head_attention_2/value/addAddV23multi_head_attention_2/value/einsum/Einsum:output:07multi_head_attention_2/value/add/ReadVariableOp:value:0*
T0*/
_output_shapes
:���������da
multi_head_attention_2/Mul/yConst*
_output_shapes
: *
dtype0*
valueB
 *   ?�
multi_head_attention_2/MulMul$multi_head_attention_2/query/add:z:0%multi_head_attention_2/Mul/y:output:0*
T0*/
_output_shapes
:���������d�
$multi_head_attention_2/einsum/EinsumEinsum"multi_head_attention_2/key/add:z:0multi_head_attention_2/Mul:z:0*
N*
T0*/
_output_shapes
:���������dd*
equationaecd,abcd->acbe�
&multi_head_attention_2/softmax/SoftmaxSoftmax-multi_head_attention_2/einsum/Einsum:output:0*
T0*/
_output_shapes
:���������dd�
'multi_head_attention_2/dropout/IdentityIdentity0multi_head_attention_2/softmax/Softmax:softmax:0*
T0*/
_output_shapes
:���������dd�
&multi_head_attention_2/einsum_1/EinsumEinsum0multi_head_attention_2/dropout/Identity:output:0$multi_head_attention_2/value/add:z:0*
N*
T0*/
_output_shapes
:���������d*
equationacbe,aecd->abcd�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpReadVariableOpMmulti_head_attention_2_attention_output_einsum_einsum_readvariableop_resource*"
_output_shapes
:*
dtype0�
5multi_head_attention_2/attention_output/einsum/EinsumEinsum/multi_head_attention_2/einsum_1/Einsum:output:0Lmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp:value:0*
N*
T0*+
_output_shapes
:���������d*
equationabcd,cde->abe�
:multi_head_attention_2/attention_output/add/ReadVariableOpReadVariableOpCmulti_head_attention_2_attention_output_add_readvariableop_resource*
_output_shapes
:*
dtype0�
+multi_head_attention_2/attention_output/addAddV2>multi_head_attention_2/attention_output/einsum/Einsum:output:0Bmulti_head_attention_2/attention_output/add/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
dropout_9/IdentityIdentity/multi_head_attention_2/attention_output/add:z:0*
T0*+
_output_shapes
:���������dg
addAddV2inputsdropout_9/Identity:output:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_4/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_4/moments/meanMeanadd:z:0=layer_normalization_4/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_4/moments/StopGradientStopGradient+layer_normalization_4/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_4/moments/SquaredDifferenceSquaredDifferenceadd:z:03layer_normalization_4/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_4/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_4/moments/varianceMean3layer_normalization_4/moments/SquaredDifference:z:0Alayer_normalization_4/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_4/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_4/batchnorm/addAddV2/layer_normalization_4/moments/variance:output:0.layer_normalization_4/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/RsqrtRsqrt'layer_normalization_4/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_4/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_4_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/mulMul)layer_normalization_4/batchnorm/Rsqrt:y:0:layer_normalization_4/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_1Muladd:z:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/mul_2Mul+layer_normalization_4/moments/mean:output:0'layer_normalization_4/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_4/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_4_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_4/batchnorm/subSub6layer_normalization_4/batchnorm/ReadVariableOp:value:0)layer_normalization_4/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_4/batchnorm/add_1AddV2)layer_normalization_4/batchnorm/mul_1:z:0'layer_normalization_4/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_8/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       }
$sequential_2/dense_8/Tensordot/ShapeShape)layer_normalization_4/batchnorm/add_1:z:0*
T0*
_output_shapes
:n
,sequential_2/dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/GatherV2GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/free:output:05sequential_2/dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_8/Tensordot/GatherV2_1GatherV2-sequential_2/dense_8/Tensordot/Shape:output:0,sequential_2/dense_8/Tensordot/axes:output:07sequential_2/dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_8/Tensordot/ProdProd0sequential_2/dense_8/Tensordot/GatherV2:output:0-sequential_2/dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_8/Tensordot/Prod_1Prod2sequential_2/dense_8/Tensordot/GatherV2_1:output:0/sequential_2/dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_8/Tensordot/concatConcatV2,sequential_2/dense_8/Tensordot/free:output:0,sequential_2/dense_8/Tensordot/axes:output:03sequential_2/dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_8/Tensordot/stackPack,sequential_2/dense_8/Tensordot/Prod:output:0.sequential_2/dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_8/Tensordot/transpose	Transpose)layer_normalization_4/batchnorm/add_1:z:0.sequential_2/dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_8/Tensordot/ReshapeReshape,sequential_2/dense_8/Tensordot/transpose:y:0-sequential_2/dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_8/Tensordot/MatMulMatMul/sequential_2/dense_8/Tensordot/Reshape:output:05sequential_2/dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_8/Tensordot/concat_1ConcatV20sequential_2/dense_8/Tensordot/GatherV2:output:0/sequential_2/dense_8/Tensordot/Const_2:output:05sequential_2/dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_8/TensordotReshape/sequential_2/dense_8/Tensordot/MatMul:product:00sequential_2/dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_8/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_8/BiasAddBiasAdd'sequential_2/dense_8/Tensordot:output:03sequential_2/dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d~
sequential_2/dense_8/ReluRelu%sequential_2/dense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
-sequential_2/dense_9/Tensordot/ReadVariableOpReadVariableOp6sequential_2_dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0m
#sequential_2/dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:t
#sequential_2/dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       {
$sequential_2/dense_9/Tensordot/ShapeShape'sequential_2/dense_8/Relu:activations:0*
T0*
_output_shapes
:n
,sequential_2/dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/GatherV2GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/free:output:05sequential_2/dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:p
.sequential_2/dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
)sequential_2/dense_9/Tensordot/GatherV2_1GatherV2-sequential_2/dense_9/Tensordot/Shape:output:0,sequential_2/dense_9/Tensordot/axes:output:07sequential_2/dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:n
$sequential_2/dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
#sequential_2/dense_9/Tensordot/ProdProd0sequential_2/dense_9/Tensordot/GatherV2:output:0-sequential_2/dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: p
&sequential_2/dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
%sequential_2/dense_9/Tensordot/Prod_1Prod2sequential_2/dense_9/Tensordot/GatherV2_1:output:0/sequential_2/dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: l
*sequential_2/dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
%sequential_2/dense_9/Tensordot/concatConcatV2,sequential_2/dense_9/Tensordot/free:output:0,sequential_2/dense_9/Tensordot/axes:output:03sequential_2/dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
$sequential_2/dense_9/Tensordot/stackPack,sequential_2/dense_9/Tensordot/Prod:output:0.sequential_2/dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
(sequential_2/dense_9/Tensordot/transpose	Transpose'sequential_2/dense_8/Relu:activations:0.sequential_2/dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
&sequential_2/dense_9/Tensordot/ReshapeReshape,sequential_2/dense_9/Tensordot/transpose:y:0-sequential_2/dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
%sequential_2/dense_9/Tensordot/MatMulMatMul/sequential_2/dense_9/Tensordot/Reshape:output:05sequential_2/dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������p
&sequential_2/dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:n
,sequential_2/dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
'sequential_2/dense_9/Tensordot/concat_1ConcatV20sequential_2/dense_9/Tensordot/GatherV2:output:0/sequential_2/dense_9/Tensordot/Const_2:output:05sequential_2/dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
sequential_2/dense_9/TensordotReshape/sequential_2/dense_9/Tensordot/MatMul:product:00sequential_2/dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
+sequential_2/dense_9/BiasAdd/ReadVariableOpReadVariableOp4sequential_2_dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
sequential_2/dense_9/BiasAddBiasAdd'sequential_2/dense_9/Tensordot:output:03sequential_2/dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d|
dropout_10/IdentityIdentity%sequential_2/dense_9/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
add_1AddV2)layer_normalization_4/batchnorm/add_1:z:0dropout_10/Identity:output:0*
T0*+
_output_shapes
:���������d~
4layer_normalization_5/moments/mean/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
"layer_normalization_5/moments/meanMean	add_1:z:0=layer_normalization_5/moments/mean/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(�
*layer_normalization_5/moments/StopGradientStopGradient+layer_normalization_5/moments/mean:output:0*
T0*+
_output_shapes
:���������d�
/layer_normalization_5/moments/SquaredDifferenceSquaredDifference	add_1:z:03layer_normalization_5/moments/StopGradient:output:0*
T0*+
_output_shapes
:���������d�
8layer_normalization_5/moments/variance/reduction_indicesConst*
_output_shapes
:*
dtype0*
valueB:�
&layer_normalization_5/moments/varianceMean3layer_normalization_5/moments/SquaredDifference:z:0Alayer_normalization_5/moments/variance/reduction_indices:output:0*
T0*+
_output_shapes
:���������d*
	keep_dims(j
%layer_normalization_5/batchnorm/add/yConst*
_output_shapes
: *
dtype0*
valueB
 *�7�5�
#layer_normalization_5/batchnorm/addAddV2/layer_normalization_5/moments/variance:output:0.layer_normalization_5/batchnorm/add/y:output:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/RsqrtRsqrt'layer_normalization_5/batchnorm/add:z:0*
T0*+
_output_shapes
:���������d�
2layer_normalization_5/batchnorm/mul/ReadVariableOpReadVariableOp;layer_normalization_5_batchnorm_mul_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/mulMul)layer_normalization_5/batchnorm/Rsqrt:y:0:layer_normalization_5/batchnorm/mul/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_1Mul	add_1:z:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/mul_2Mul+layer_normalization_5/moments/mean:output:0'layer_normalization_5/batchnorm/mul:z:0*
T0*+
_output_shapes
:���������d�
.layer_normalization_5/batchnorm/ReadVariableOpReadVariableOp7layer_normalization_5_batchnorm_readvariableop_resource*
_output_shapes
:*
dtype0�
#layer_normalization_5/batchnorm/subSub6layer_normalization_5/batchnorm/ReadVariableOp:value:0)layer_normalization_5/batchnorm/mul_2:z:0*
T0*+
_output_shapes
:���������d�
%layer_normalization_5/batchnorm/add_1AddV2)layer_normalization_5/batchnorm/mul_1:z:0'layer_normalization_5/batchnorm/sub:z:0*
T0*+
_output_shapes
:���������d|
IdentityIdentity)layer_normalization_5/batchnorm/add_1:z:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp/^layer_normalization_4/batchnorm/ReadVariableOp3^layer_normalization_4/batchnorm/mul/ReadVariableOp/^layer_normalization_5/batchnorm/ReadVariableOp3^layer_normalization_5/batchnorm/mul/ReadVariableOp;^multi_head_attention_2/attention_output/add/ReadVariableOpE^multi_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp.^multi_head_attention_2/key/add/ReadVariableOp8^multi_head_attention_2/key/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/query/add/ReadVariableOp:^multi_head_attention_2/query/einsum/Einsum/ReadVariableOp0^multi_head_attention_2/value/add/ReadVariableOp:^multi_head_attention_2/value/einsum/Einsum/ReadVariableOp,^sequential_2/dense_8/BiasAdd/ReadVariableOp.^sequential_2/dense_8/Tensordot/ReadVariableOp,^sequential_2/dense_9/BiasAdd/ReadVariableOp.^sequential_2/dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 2`
.layer_normalization_4/batchnorm/ReadVariableOp.layer_normalization_4/batchnorm/ReadVariableOp2h
2layer_normalization_4/batchnorm/mul/ReadVariableOp2layer_normalization_4/batchnorm/mul/ReadVariableOp2`
.layer_normalization_5/batchnorm/ReadVariableOp.layer_normalization_5/batchnorm/ReadVariableOp2h
2layer_normalization_5/batchnorm/mul/ReadVariableOp2layer_normalization_5/batchnorm/mul/ReadVariableOp2x
:multi_head_attention_2/attention_output/add/ReadVariableOp:multi_head_attention_2/attention_output/add/ReadVariableOp2�
Dmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOpDmulti_head_attention_2/attention_output/einsum/Einsum/ReadVariableOp2^
-multi_head_attention_2/key/add/ReadVariableOp-multi_head_attention_2/key/add/ReadVariableOp2r
7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp7multi_head_attention_2/key/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/query/add/ReadVariableOp/multi_head_attention_2/query/add/ReadVariableOp2v
9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp9multi_head_attention_2/query/einsum/Einsum/ReadVariableOp2b
/multi_head_attention_2/value/add/ReadVariableOp/multi_head_attention_2/value/add/ReadVariableOp2v
9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp9multi_head_attention_2/value/einsum/Einsum/ReadVariableOp2Z
+sequential_2/dense_8/BiasAdd/ReadVariableOp+sequential_2/dense_8/BiasAdd/ReadVariableOp2^
-sequential_2/dense_8/Tensordot/ReadVariableOp-sequential_2/dense_8/Tensordot/ReadVariableOp2Z
+sequential_2/dense_9/BiasAdd/ReadVariableOp+sequential_2/dense_9/BiasAdd/ReadVariableOp2^
-sequential_2/dense_9/Tensordot/ReadVariableOp-sequential_2/dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�>
�
G__inference_sequential_2_layer_call_and_return_conditional_losses_54656

inputs;
)dense_8_tensordot_readvariableop_resource:5
'dense_8_biasadd_readvariableop_resource:;
)dense_9_tensordot_readvariableop_resource:5
'dense_9_biasadd_readvariableop_resource:
identity��dense_8/BiasAdd/ReadVariableOp� dense_8/Tensordot/ReadVariableOp�dense_9/BiasAdd/ReadVariableOp� dense_9/Tensordot/ReadVariableOp�
 dense_8/Tensordot/ReadVariableOpReadVariableOp)dense_8_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0`
dense_8/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:g
dense_8/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       M
dense_8/Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:a
dense_8/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/GatherV2GatherV2 dense_8/Tensordot/Shape:output:0dense_8/Tensordot/free:output:0(dense_8/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:c
!dense_8/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/GatherV2_1GatherV2 dense_8/Tensordot/Shape:output:0dense_8/Tensordot/axes:output:0*dense_8/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:a
dense_8/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
dense_8/Tensordot/ProdProd#dense_8/Tensordot/GatherV2:output:0 dense_8/Tensordot/Const:output:0*
T0*
_output_shapes
: c
dense_8/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
dense_8/Tensordot/Prod_1Prod%dense_8/Tensordot/GatherV2_1:output:0"dense_8/Tensordot/Const_1:output:0*
T0*
_output_shapes
: _
dense_8/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/concatConcatV2dense_8/Tensordot/free:output:0dense_8/Tensordot/axes:output:0&dense_8/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
dense_8/Tensordot/stackPackdense_8/Tensordot/Prod:output:0!dense_8/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
dense_8/Tensordot/transpose	Transposeinputs!dense_8/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
dense_8/Tensordot/ReshapeReshapedense_8/Tensordot/transpose:y:0 dense_8/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
dense_8/Tensordot/MatMulMatMul"dense_8/Tensordot/Reshape:output:0(dense_8/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������c
dense_8/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:a
dense_8/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_8/Tensordot/concat_1ConcatV2#dense_8/Tensordot/GatherV2:output:0"dense_8/Tensordot/Const_2:output:0(dense_8/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
dense_8/TensordotReshape"dense_8/Tensordot/MatMul:product:0#dense_8/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
dense_8/BiasAdd/ReadVariableOpReadVariableOp'dense_8_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_8/BiasAddBiasAdddense_8/Tensordot:output:0&dense_8/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dd
dense_8/ReluReludense_8/BiasAdd:output:0*
T0*+
_output_shapes
:���������d�
 dense_9/Tensordot/ReadVariableOpReadVariableOp)dense_9_tensordot_readvariableop_resource*
_output_shapes

:*
dtype0`
dense_9/Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:g
dense_9/Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       a
dense_9/Tensordot/ShapeShapedense_8/Relu:activations:0*
T0*
_output_shapes
:a
dense_9/Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/GatherV2GatherV2 dense_9/Tensordot/Shape:output:0dense_9/Tensordot/free:output:0(dense_9/Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:c
!dense_9/Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/GatherV2_1GatherV2 dense_9/Tensordot/Shape:output:0dense_9/Tensordot/axes:output:0*dense_9/Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:a
dense_9/Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: �
dense_9/Tensordot/ProdProd#dense_9/Tensordot/GatherV2:output:0 dense_9/Tensordot/Const:output:0*
T0*
_output_shapes
: c
dense_9/Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: �
dense_9/Tensordot/Prod_1Prod%dense_9/Tensordot/GatherV2_1:output:0"dense_9/Tensordot/Const_1:output:0*
T0*
_output_shapes
: _
dense_9/Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/concatConcatV2dense_9/Tensordot/free:output:0dense_9/Tensordot/axes:output:0&dense_9/Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:�
dense_9/Tensordot/stackPackdense_9/Tensordot/Prod:output:0!dense_9/Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:�
dense_9/Tensordot/transpose	Transposedense_8/Relu:activations:0!dense_9/Tensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
dense_9/Tensordot/ReshapeReshapedense_9/Tensordot/transpose:y:0 dense_9/Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
dense_9/Tensordot/MatMulMatMul"dense_9/Tensordot/Reshape:output:0(dense_9/Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������c
dense_9/Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:a
dense_9/Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
dense_9/Tensordot/concat_1ConcatV2#dense_9/Tensordot/GatherV2:output:0"dense_9/Tensordot/Const_2:output:0(dense_9/Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
dense_9/TensordotReshape"dense_9/Tensordot/MatMul:product:0#dense_9/Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������d�
dense_9/BiasAdd/ReadVariableOpReadVariableOp'dense_9_biasadd_readvariableop_resource*
_output_shapes
:*
dtype0�
dense_9/BiasAddBiasAdddense_9/Tensordot:output:0&dense_9/BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dk
IdentityIdentitydense_9/BiasAdd:output:0^NoOp*
T0*+
_output_shapes
:���������d�
NoOpNoOp^dense_8/BiasAdd/ReadVariableOp!^dense_8/Tensordot/ReadVariableOp^dense_9/BiasAdd/ReadVariableOp!^dense_9/Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*2
_input_shapes!
:���������d: : : : 2@
dense_8/BiasAdd/ReadVariableOpdense_8/BiasAdd/ReadVariableOp2D
 dense_8/Tensordot/ReadVariableOp dense_8/Tensordot/ReadVariableOp2@
dense_9/BiasAdd/ReadVariableOpdense_9/BiasAdd/ReadVariableOp2D
 dense_9/Tensordot/ReadVariableOp dense_9/Tensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
(__inference_dense_10_layer_call_fn_54515

inputs
unknown:
	unknown_0:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0*
Tin
2*
Tout
2*
_collective_manager_ids
 *'
_output_shapes
:���������*$
_read_only_resource_inputs
*-
config_proto

CPU

GPU 2J 8� *L
fGRE
C__inference_dense_10_layer_call_and_return_conditional_losses_52901o
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*'
_output_shapes
:���������`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime**
_input_shapes
:���������: : 22
StatefulPartitionedCallStatefulPartitionedCall:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
c
E__inference_dropout_11_layer_call_and_return_conditional_losses_54494

inputs

identity_1N
IdentityIdentityinputs*
T0*'
_output_shapes
:���������[

Identity_1IdentityIdentity:output:0*
T0*'
_output_shapes
:���������"!

identity_1Identity_1:output:0*(
_construction_contextkEagerRuntime*&
_input_shapes
:���������:O K
'
_output_shapes
:���������
 
_user_specified_nameinputs
�
�
B__inference_dense_9_layer_call_and_return_conditional_losses_52552

inputs3
!tensordot_readvariableop_resource:-
biasadd_readvariableop_resource:
identity��BiasAdd/ReadVariableOp�Tensordot/ReadVariableOpz
Tensordot/ReadVariableOpReadVariableOp!tensordot_readvariableop_resource*
_output_shapes

:*
dtype0X
Tensordot/axesConst*
_output_shapes
:*
dtype0*
valueB:_
Tensordot/freeConst*
_output_shapes
:*
dtype0*
valueB"       E
Tensordot/ShapeShapeinputs*
T0*
_output_shapes
:Y
Tensordot/GatherV2/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2GatherV2Tensordot/Shape:output:0Tensordot/free:output:0 Tensordot/GatherV2/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:[
Tensordot/GatherV2_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/GatherV2_1GatherV2Tensordot/Shape:output:0Tensordot/axes:output:0"Tensordot/GatherV2_1/axis:output:0*
Taxis0*
Tindices0*
Tparams0*
_output_shapes
:Y
Tensordot/ConstConst*
_output_shapes
:*
dtype0*
valueB: n
Tensordot/ProdProdTensordot/GatherV2:output:0Tensordot/Const:output:0*
T0*
_output_shapes
: [
Tensordot/Const_1Const*
_output_shapes
:*
dtype0*
valueB: t
Tensordot/Prod_1ProdTensordot/GatherV2_1:output:0Tensordot/Const_1:output:0*
T0*
_output_shapes
: W
Tensordot/concat/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concatConcatV2Tensordot/free:output:0Tensordot/axes:output:0Tensordot/concat/axis:output:0*
N*
T0*
_output_shapes
:y
Tensordot/stackPackTensordot/Prod:output:0Tensordot/Prod_1:output:0*
N*
T0*
_output_shapes
:y
Tensordot/transpose	TransposeinputsTensordot/concat:output:0*
T0*+
_output_shapes
:���������d�
Tensordot/ReshapeReshapeTensordot/transpose:y:0Tensordot/stack:output:0*
T0*0
_output_shapes
:�������������������
Tensordot/MatMulMatMulTensordot/Reshape:output:0 Tensordot/ReadVariableOp:value:0*
T0*'
_output_shapes
:���������[
Tensordot/Const_2Const*
_output_shapes
:*
dtype0*
valueB:Y
Tensordot/concat_1/axisConst*
_output_shapes
: *
dtype0*
value	B : �
Tensordot/concat_1ConcatV2Tensordot/GatherV2:output:0Tensordot/Const_2:output:0 Tensordot/concat_1/axis:output:0*
N*
T0*
_output_shapes
:�
	TensordotReshapeTensordot/MatMul:product:0Tensordot/concat_1:output:0*
T0*+
_output_shapes
:���������dr
BiasAdd/ReadVariableOpReadVariableOpbiasadd_readvariableop_resource*
_output_shapes
:*
dtype0|
BiasAddBiasAddTensordot:output:0BiasAdd/ReadVariableOp:value:0*
T0*+
_output_shapes
:���������dc
IdentityIdentityBiasAdd:output:0^NoOp*
T0*+
_output_shapes
:���������dz
NoOpNoOp^BiasAdd/ReadVariableOp^Tensordot/ReadVariableOp*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*.
_input_shapes
:���������d: : 20
BiasAdd/ReadVariableOpBiasAdd/ReadVariableOp24
Tensordot/ReadVariableOpTensordot/ReadVariableOp:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs
�
�
3__inference_transformer_block_2_layer_call_fn_54164

inputs
unknown:
	unknown_0:
	unknown_1:
	unknown_2:
	unknown_3:
	unknown_4:
	unknown_5:
	unknown_6:
	unknown_7:
	unknown_8:
	unknown_9:

unknown_10:

unknown_11:

unknown_12:

unknown_13:

unknown_14:
identity��StatefulPartitionedCall�
StatefulPartitionedCallStatefulPartitionedCallinputsunknown	unknown_0	unknown_1	unknown_2	unknown_3	unknown_4	unknown_5	unknown_6	unknown_7	unknown_8	unknown_9
unknown_10
unknown_11
unknown_12
unknown_13
unknown_14*
Tin
2*
Tout
2*
_collective_manager_ids
 *+
_output_shapes
:���������d*2
_read_only_resource_inputs
	
*-
config_proto

CPU

GPU 2J 8� *W
fRRP
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_52848s
IdentityIdentity StatefulPartitionedCall:output:0^NoOp*
T0*+
_output_shapes
:���������d`
NoOpNoOp^StatefulPartitionedCall*"
_acd_function_control_output(*
_output_shapes
 "
identityIdentity:output:0*(
_construction_contextkEagerRuntime*J
_input_shapes9
7:���������d: : : : : : : : : : : : : : : : 22
StatefulPartitionedCallStatefulPartitionedCall:S O
+
_output_shapes
:���������d
 
_user_specified_nameinputs"�	L
saver_filename:0StatefulPartitionedCall_1:0StatefulPartitionedCall_28"
saved_model_main_op

NoOp*>
__saved_model_init_op%#
__saved_model_init_op

NoOp*�
serving_default�
;
input_30
serving_default_input_3:0���������d<
dense_110
StatefulPartitionedCall:0���������tensorflow/serving/predict:η
�
layer-0
layer_with_weights-0
layer-1
layer_with_weights-1
layer-2
layer-3
layer-4
layer_with_weights-2
layer-5
layer-6
layer_with_weights-3
layer-7
		variables

trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
_default_save_signature
	optimizer

signatures"
_tf_keras_network
"
_tf_keras_input_layer
�
	variables
trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
	token_emb
pos_emb"
_tf_keras_layer
�
	variables
trainable_variables
regularization_losses
	keras_api
__call__
*&call_and_return_all_conditional_losses
 att
!ffn
"
layernorm1
#
layernorm2
$dropout1
%dropout2"
_tf_keras_layer
�
&	variables
'trainable_variables
(regularization_losses
)	keras_api
*__call__
*+&call_and_return_all_conditional_losses"
_tf_keras_layer
�
,	variables
-trainable_variables
.regularization_losses
/	keras_api
0__call__
*1&call_and_return_all_conditional_losses
2_random_generator"
_tf_keras_layer
�
3	variables
4trainable_variables
5regularization_losses
6	keras_api
7__call__
*8&call_and_return_all_conditional_losses

9kernel
:bias"
_tf_keras_layer
�
;	variables
<trainable_variables
=regularization_losses
>	keras_api
?__call__
*@&call_and_return_all_conditional_losses
A_random_generator"
_tf_keras_layer
�
B	variables
Ctrainable_variables
Dregularization_losses
E	keras_api
F__call__
*G&call_and_return_all_conditional_losses

Hkernel
Ibias"
_tf_keras_layer
�
J0
K1
L2
M3
N4
O5
P6
Q7
R8
S9
T10
U11
V12
W13
X14
Y15
Z16
[17
918
:19
H20
I21"
trackable_list_wrapper
�
J0
K1
L2
M3
N4
O5
P6
Q7
R8
S9
T10
U11
V12
W13
X14
Y15
Z16
[17
918
:19
H20
I21"
trackable_list_wrapper
 "
trackable_list_wrapper
�
\non_trainable_variables

]layers
^metrics
_layer_regularization_losses
`layer_metrics
		variables

trainable_variables
regularization_losses
__call__
_default_save_signature
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses"
_generic_user_object
�
atrace_0
btrace_1
ctrace_2
dtrace_32�
'__inference_model_2_layer_call_fn_52979
'__inference_model_2_layer_call_fn_53688
'__inference_model_2_layer_call_fn_53737
'__inference_model_2_layer_call_fn_53472�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 zatrace_0zbtrace_1zctrace_2zdtrace_3
�
etrace_0
ftrace_1
gtrace_2
htrace_32�
B__inference_model_2_layer_call_and_return_conditional_losses_53902
B__inference_model_2_layer_call_and_return_conditional_losses_54094
B__inference_model_2_layer_call_and_return_conditional_losses_53527
B__inference_model_2_layer_call_and_return_conditional_losses_53582�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 zetrace_0zftrace_1zgtrace_2zhtrace_3
�B�
 __inference__wrapped_model_52478input_3"�
���
FullArgSpec
args� 
varargsjargs
varkwjkwargs
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�
iiter

jbeta_1

kbeta_2
	ldecay
mlearning_rate9m�:m�Hm�Im�Jm�Km�Lm�Mm�Nm�Om�Pm�Qm�Rm�Sm�Tm�Um�Vm�Wm�Xm�Ym�Zm�[m�9v�:v�Hv�Iv�Jv�Kv�Lv�Mv�Nv�Ov�Pv�Qv�Rv�Sv�Tv�Uv�Vv�Wv�Xv�Yv�Zv�[v�"
	optimizer
,
nserving_default"
signature_map
.
J0
K1"
trackable_list_wrapper
.
J0
K1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
onon_trainable_variables

players
qmetrics
rlayer_regularization_losses
slayer_metrics
	variables
trainable_variables
regularization_losses
__call__
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses"
_generic_user_object
�
ttrace_02�
>__inference_token_and_position_embedding_2_layer_call_fn_54103�
���
FullArgSpec
args�
jself
jx
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 zttrace_0
�
utrace_02�
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_54127�
���
FullArgSpec
args�
jself
jx
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 zutrace_0
�
v	variables
wtrainable_variables
xregularization_losses
y	keras_api
z__call__
*{&call_and_return_all_conditional_losses
J
embeddings"
_tf_keras_layer
�
|	variables
}trainable_variables
~regularization_losses
	keras_api
�__call__
+�&call_and_return_all_conditional_losses
K
embeddings"
_tf_keras_layer
�
L0
M1
N2
O3
P4
Q5
R6
S7
T8
U9
V10
W11
X12
Y13
Z14
[15"
trackable_list_wrapper
�
L0
M1
N2
O3
P4
Q5
R6
S7
T8
U9
V10
W11
X12
Y13
Z14
[15"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
	variables
trainable_variables
regularization_losses
__call__
*&call_and_return_all_conditional_losses
&"call_and_return_conditional_losses"
_generic_user_object
�
�trace_0
�trace_12�
3__inference_transformer_block_2_layer_call_fn_54164
3__inference_transformer_block_2_layer_call_fn_54201�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
�
�trace_0
�trace_12�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54328
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54468�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_query_dense
�
_key_dense
�_value_dense
�_softmax
�_dropout_layer
�_output_dense"
_tf_keras_layer
�
�layer_with_weights-0
�layer-0
�layer_with_weights-1
�layer-1
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses"
_tf_keras_sequential
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
	�axis
	Xgamma
Ybeta"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
	�axis
	Zgamma
[beta"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator"
_tf_keras_layer
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
&	variables
'trainable_variables
(regularization_losses
*__call__
*+&call_and_return_all_conditional_losses
&+"call_and_return_conditional_losses"
_generic_user_object
�
�trace_02�
:__inference_global_average_pooling1d_2_layer_call_fn_54473�
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
�
�trace_02�
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_54479�
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
,	variables
-trainable_variables
.regularization_losses
0__call__
*1&call_and_return_all_conditional_losses
&1"call_and_return_conditional_losses"
_generic_user_object
�
�trace_0
�trace_12�
*__inference_dropout_11_layer_call_fn_54484
*__inference_dropout_11_layer_call_fn_54489�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
�
�trace_0
�trace_12�
E__inference_dropout_11_layer_call_and_return_conditional_losses_54494
E__inference_dropout_11_layer_call_and_return_conditional_losses_54506�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
"
_generic_user_object
.
90
:1"
trackable_list_wrapper
.
90
:1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
3	variables
4trainable_variables
5regularization_losses
7__call__
*8&call_and_return_all_conditional_losses
&8"call_and_return_conditional_losses"
_generic_user_object
�
�trace_02�
(__inference_dense_10_layer_call_fn_54515�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
�
�trace_02�
C__inference_dense_10_layer_call_and_return_conditional_losses_54526�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
!:2dense_10/kernel
:2dense_10/bias
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
;	variables
<trainable_variables
=regularization_losses
?__call__
*@&call_and_return_all_conditional_losses
&@"call_and_return_conditional_losses"
_generic_user_object
�
�trace_0
�trace_12�
*__inference_dropout_12_layer_call_fn_54531
*__inference_dropout_12_layer_call_fn_54536�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
�
�trace_0
�trace_12�
E__inference_dropout_12_layer_call_and_return_conditional_losses_54541
E__inference_dropout_12_layer_call_and_return_conditional_losses_54553�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1
"
_generic_user_object
.
H0
I1"
trackable_list_wrapper
.
H0
I1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
B	variables
Ctrainable_variables
Dregularization_losses
F__call__
*G&call_and_return_all_conditional_losses
&G"call_and_return_conditional_losses"
_generic_user_object
�
�trace_02�
(__inference_dense_11_layer_call_fn_54562�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
�
�trace_02�
C__inference_dense_11_layer_call_and_return_conditional_losses_54573�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
!:2dense_11/kernel
:2dense_11/bias
H:F	�25token_and_position_embedding_2/embedding_4/embeddings
G:Ed25token_and_position_embedding_2/embedding_5/embeddings
M:K27transformer_block_2/multi_head_attention_2/query/kernel
G:E25transformer_block_2/multi_head_attention_2/query/bias
K:I25transformer_block_2/multi_head_attention_2/key/kernel
E:C23transformer_block_2/multi_head_attention_2/key/bias
M:K27transformer_block_2/multi_head_attention_2/value/kernel
G:E25transformer_block_2/multi_head_attention_2/value/bias
X:V2Btransformer_block_2/multi_head_attention_2/attention_output/kernel
N:L2@transformer_block_2/multi_head_attention_2/attention_output/bias
 :2dense_8/kernel
:2dense_8/bias
 :2dense_9/kernel
:2dense_9/bias
=:;2/transformer_block_2/layer_normalization_4/gamma
<::2.transformer_block_2/layer_normalization_4/beta
=:;2/transformer_block_2/layer_normalization_5/gamma
<::2.transformer_block_2/layer_normalization_5/beta
 "
trackable_list_wrapper
X
0
1
2
3
4
5
6
7"
trackable_list_wrapper
0
�0
�1"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
'__inference_model_2_layer_call_fn_52979input_3"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
'__inference_model_2_layer_call_fn_53688inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
'__inference_model_2_layer_call_fn_53737inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
'__inference_model_2_layer_call_fn_53472input_3"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_model_2_layer_call_and_return_conditional_losses_53902inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_model_2_layer_call_and_return_conditional_losses_54094inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_model_2_layer_call_and_return_conditional_losses_53527input_3"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_model_2_layer_call_and_return_conditional_losses_53582input_3"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
:	 (2	Adam/iter
: (2Adam/beta_1
: (2Adam/beta_2
: (2
Adam/decay
: (2Adam/learning_rate
�B�
#__inference_signature_wrapper_53639input_3"�
���
FullArgSpec
args� 
varargs
 
varkwjkwargs
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
.
0
1"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
>__inference_token_and_position_embedding_2_layer_call_fn_54103x"�
���
FullArgSpec
args�
jself
jx
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_54127x"�
���
FullArgSpec
args�
jself
jx
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
'
J0"
trackable_list_wrapper
'
J0"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
v	variables
wtrainable_variables
xregularization_losses
z__call__
*{&call_and_return_all_conditional_losses
&{"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
'
K0"
trackable_list_wrapper
'
K0"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
|	variables
}trainable_variables
~regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
J
 0
!1
"2
#3
$4
%5"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
3__inference_transformer_block_2_layer_call_fn_54164inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
3__inference_transformer_block_2_layer_call_fn_54201inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54328inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54468inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
X
L0
M1
N2
O3
P4
Q5
R6
S7"
trackable_list_wrapper
X
L0
M1
N2
O3
P4
Q5
R6
S7"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpecx
argsp�m
jself
jquery
jvalue
jkey
jattention_mask
jreturn_attention_scores

jtraining
juse_causal_mask
varargs
 
varkw
 #
defaults�

 

 
p 
p 
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpecx
argsp�m
jself
jquery
jvalue
jkey
jattention_mask
jreturn_attention_scores

jtraining
juse_causal_mask
varargs
 
varkw
 #
defaults�

 

 
p 
p 
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Lkernel
Mbias"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Nkernel
Obias"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Pkernel
Qbias"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�_random_generator"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses
�partial_output_shape
�full_output_shape

Rkernel
Sbias"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses

Tkernel
Ubias"
_tf_keras_layer
�
�	variables
�trainable_variables
�regularization_losses
�	keras_api
�__call__
+�&call_and_return_all_conditional_losses

Vkernel
Wbias"
_tf_keras_layer
<
T0
U1
V2
W3"
trackable_list_wrapper
<
T0
U1
V2
W3"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�
�trace_0
�trace_1
�trace_2
�trace_32�
,__inference_sequential_2_layer_call_fn_52570
,__inference_sequential_2_layer_call_fn_54586
,__inference_sequential_2_layer_call_fn_54599
,__inference_sequential_2_layer_call_fn_52643�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1z�trace_2z�trace_3
�
�trace_0
�trace_1
�trace_2
�trace_32�
G__inference_sequential_2_layer_call_and_return_conditional_losses_54656
G__inference_sequential_2_layer_call_and_return_conditional_losses_54713
G__inference_sequential_2_layer_call_and_return_conditional_losses_52657
G__inference_sequential_2_layer_call_and_return_conditional_losses_52671�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0z�trace_1z�trace_2z�trace_3
.
X0
Y1"
trackable_list_wrapper
.
X0
Y1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
.
Z0
[1"
trackable_list_wrapper
.
Z0
[1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
"
_generic_user_object
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
"
_generic_user_object
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
:__inference_global_average_pooling1d_2_layer_call_fn_54473inputs"�
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_54479inputs"�
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
*__inference_dropout_11_layer_call_fn_54484inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
*__inference_dropout_11_layer_call_fn_54489inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
E__inference_dropout_11_layer_call_and_return_conditional_losses_54494inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
E__inference_dropout_11_layer_call_and_return_conditional_losses_54506inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
(__inference_dense_10_layer_call_fn_54515inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
C__inference_dense_10_layer_call_and_return_conditional_losses_54526inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
*__inference_dropout_12_layer_call_fn_54531inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
*__inference_dropout_12_layer_call_fn_54536inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
E__inference_dropout_12_layer_call_and_return_conditional_losses_54541inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
E__inference_dropout_12_layer_call_and_return_conditional_losses_54553inputs"�
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
(__inference_dense_11_layer_call_fn_54562inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
C__inference_dense_11_layer_call_and_return_conditional_losses_54573inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
R
�	variables
�	keras_api

�total

�count"
_tf_keras_metric
c
�	variables
�	keras_api

�total

�count
�
_fn_kwargs"
_tf_keras_metric
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
P
�0
�1
�2
�3
�4
�5"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
.
L0
M1"
trackable_list_wrapper
.
L0
M1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
.
N0
O1"
trackable_list_wrapper
.
N0
O1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
.
P0
Q1"
trackable_list_wrapper
.
P0
Q1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec%
args�
jself
jinputs
jmask
varargs
 
varkw
 
defaults�

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec)
args!�
jself
jinputs

jtraining
varargs
 
varkw
 
defaults�
p 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
"
_generic_user_object
.
R0
S1"
trackable_list_wrapper
.
R0
S1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�2��
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
.
T0
U1"
trackable_list_wrapper
.
T0
U1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�
�trace_02�
'__inference_dense_8_layer_call_fn_54722�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
�
�trace_02�
B__inference_dense_8_layer_call_and_return_conditional_losses_54753�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
.
V0
W1"
trackable_list_wrapper
.
V0
W1"
trackable_list_wrapper
 "
trackable_list_wrapper
�
�non_trainable_variables
�layers
�metrics
 �layer_regularization_losses
�layer_metrics
�	variables
�trainable_variables
�regularization_losses
�__call__
+�&call_and_return_all_conditional_losses
'�"call_and_return_conditional_losses"
_generic_user_object
�
�trace_02�
'__inference_dense_9_layer_call_fn_54762�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
�
�trace_02�
B__inference_dense_9_layer_call_and_return_conditional_losses_54792�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 z�trace_0
 "
trackable_list_wrapper
0
�0
�1"
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
,__inference_sequential_2_layer_call_fn_52570dense_8_input"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
,__inference_sequential_2_layer_call_fn_54586inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
,__inference_sequential_2_layer_call_fn_54599inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
,__inference_sequential_2_layer_call_fn_52643dense_8_input"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
G__inference_sequential_2_layer_call_and_return_conditional_losses_54656inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
G__inference_sequential_2_layer_call_and_return_conditional_losses_54713inputs"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52657dense_8_input"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
G__inference_sequential_2_layer_call_and_return_conditional_losses_52671dense_8_input"�
���
FullArgSpec1
args)�&
jself
jinputs

jtraining
jmask
varargs
 
varkw
 
defaults�
p 

 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
0
�0
�1"
trackable_list_wrapper
.
�	variables"
_generic_user_object
:  (2total
:  (2count
0
�0
�1"
trackable_list_wrapper
.
�	variables"
_generic_user_object
:  (2total
:  (2count
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
'__inference_dense_8_layer_call_fn_54722inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_dense_8_layer_call_and_return_conditional_losses_54753inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_list_wrapper
 "
trackable_dict_wrapper
�B�
'__inference_dense_9_layer_call_fn_54762inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
�B�
B__inference_dense_9_layer_call_and_return_conditional_losses_54792inputs"�
���
FullArgSpec
args�
jself
jinputs
varargs
 
varkw
 
defaults
 

kwonlyargs� 
kwonlydefaults
 
annotations� *
 
&:$2Adam/dense_10/kernel/m
 :2Adam/dense_10/bias/m
&:$2Adam/dense_11/kernel/m
 :2Adam/dense_11/bias/m
M:K	�2<Adam/token_and_position_embedding_2/embedding_4/embeddings/m
L:Jd2<Adam/token_and_position_embedding_2/embedding_5/embeddings/m
R:P2>Adam/transformer_block_2/multi_head_attention_2/query/kernel/m
L:J2<Adam/transformer_block_2/multi_head_attention_2/query/bias/m
P:N2<Adam/transformer_block_2/multi_head_attention_2/key/kernel/m
J:H2:Adam/transformer_block_2/multi_head_attention_2/key/bias/m
R:P2>Adam/transformer_block_2/multi_head_attention_2/value/kernel/m
L:J2<Adam/transformer_block_2/multi_head_attention_2/value/bias/m
]:[2IAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/m
S:Q2GAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/m
%:#2Adam/dense_8/kernel/m
:2Adam/dense_8/bias/m
%:#2Adam/dense_9/kernel/m
:2Adam/dense_9/bias/m
B:@26Adam/transformer_block_2/layer_normalization_4/gamma/m
A:?25Adam/transformer_block_2/layer_normalization_4/beta/m
B:@26Adam/transformer_block_2/layer_normalization_5/gamma/m
A:?25Adam/transformer_block_2/layer_normalization_5/beta/m
&:$2Adam/dense_10/kernel/v
 :2Adam/dense_10/bias/v
&:$2Adam/dense_11/kernel/v
 :2Adam/dense_11/bias/v
M:K	�2<Adam/token_and_position_embedding_2/embedding_4/embeddings/v
L:Jd2<Adam/token_and_position_embedding_2/embedding_5/embeddings/v
R:P2>Adam/transformer_block_2/multi_head_attention_2/query/kernel/v
L:J2<Adam/transformer_block_2/multi_head_attention_2/query/bias/v
P:N2<Adam/transformer_block_2/multi_head_attention_2/key/kernel/v
J:H2:Adam/transformer_block_2/multi_head_attention_2/key/bias/v
R:P2>Adam/transformer_block_2/multi_head_attention_2/value/kernel/v
L:J2<Adam/transformer_block_2/multi_head_attention_2/value/bias/v
]:[2IAdam/transformer_block_2/multi_head_attention_2/attention_output/kernel/v
S:Q2GAdam/transformer_block_2/multi_head_attention_2/attention_output/bias/v
%:#2Adam/dense_8/kernel/v
:2Adam/dense_8/bias/v
%:#2Adam/dense_9/kernel/v
:2Adam/dense_9/bias/v
B:@26Adam/transformer_block_2/layer_normalization_4/gamma/v
A:?25Adam/transformer_block_2/layer_normalization_4/beta/v
B:@26Adam/transformer_block_2/layer_normalization_5/gamma/v
A:?25Adam/transformer_block_2/layer_normalization_5/beta/v�
 __inference__wrapped_model_52478KJLMNOPQRSXYTUVWZ[9:HI0�-
&�#
!�
input_3���������d
� "3�0
.
dense_11"�
dense_11����������
C__inference_dense_10_layer_call_and_return_conditional_losses_54526\9:/�,
%�"
 �
inputs���������
� "%�"
�
0���������
� {
(__inference_dense_10_layer_call_fn_54515O9:/�,
%�"
 �
inputs���������
� "�����������
C__inference_dense_11_layer_call_and_return_conditional_losses_54573\HI/�,
%�"
 �
inputs���������
� "%�"
�
0���������
� {
(__inference_dense_11_layer_call_fn_54562OHI/�,
%�"
 �
inputs���������
� "�����������
B__inference_dense_8_layer_call_and_return_conditional_losses_54753dTU3�0
)�&
$�!
inputs���������d
� ")�&
�
0���������d
� �
'__inference_dense_8_layer_call_fn_54722WTU3�0
)�&
$�!
inputs���������d
� "����������d�
B__inference_dense_9_layer_call_and_return_conditional_losses_54792dVW3�0
)�&
$�!
inputs���������d
� ")�&
�
0���������d
� �
'__inference_dense_9_layer_call_fn_54762WVW3�0
)�&
$�!
inputs���������d
� "����������d�
E__inference_dropout_11_layer_call_and_return_conditional_losses_54494\3�0
)�&
 �
inputs���������
p 
� "%�"
�
0���������
� �
E__inference_dropout_11_layer_call_and_return_conditional_losses_54506\3�0
)�&
 �
inputs���������
p
� "%�"
�
0���������
� }
*__inference_dropout_11_layer_call_fn_54484O3�0
)�&
 �
inputs���������
p 
� "����������}
*__inference_dropout_11_layer_call_fn_54489O3�0
)�&
 �
inputs���������
p
� "�����������
E__inference_dropout_12_layer_call_and_return_conditional_losses_54541\3�0
)�&
 �
inputs���������
p 
� "%�"
�
0���������
� �
E__inference_dropout_12_layer_call_and_return_conditional_losses_54553\3�0
)�&
 �
inputs���������
p
� "%�"
�
0���������
� }
*__inference_dropout_12_layer_call_fn_54531O3�0
)�&
 �
inputs���������
p 
� "����������}
*__inference_dropout_12_layer_call_fn_54536O3�0
)�&
 �
inputs���������
p
� "�����������
U__inference_global_average_pooling1d_2_layer_call_and_return_conditional_losses_54479{I�F
?�<
6�3
inputs'���������������������������

 
� ".�+
$�!
0������������������
� �
:__inference_global_average_pooling1d_2_layer_call_fn_54473nI�F
?�<
6�3
inputs'���������������������������

 
� "!��������������������
B__inference_model_2_layer_call_and_return_conditional_losses_53527yKJLMNOPQRSXYTUVWZ[9:HI8�5
.�+
!�
input_3���������d
p 

 
� "%�"
�
0���������
� �
B__inference_model_2_layer_call_and_return_conditional_losses_53582yKJLMNOPQRSXYTUVWZ[9:HI8�5
.�+
!�
input_3���������d
p

 
� "%�"
�
0���������
� �
B__inference_model_2_layer_call_and_return_conditional_losses_53902xKJLMNOPQRSXYTUVWZ[9:HI7�4
-�*
 �
inputs���������d
p 

 
� "%�"
�
0���������
� �
B__inference_model_2_layer_call_and_return_conditional_losses_54094xKJLMNOPQRSXYTUVWZ[9:HI7�4
-�*
 �
inputs���������d
p

 
� "%�"
�
0���������
� �
'__inference_model_2_layer_call_fn_52979lKJLMNOPQRSXYTUVWZ[9:HI8�5
.�+
!�
input_3���������d
p 

 
� "�����������
'__inference_model_2_layer_call_fn_53472lKJLMNOPQRSXYTUVWZ[9:HI8�5
.�+
!�
input_3���������d
p

 
� "�����������
'__inference_model_2_layer_call_fn_53688kKJLMNOPQRSXYTUVWZ[9:HI7�4
-�*
 �
inputs���������d
p 

 
� "�����������
'__inference_model_2_layer_call_fn_53737kKJLMNOPQRSXYTUVWZ[9:HI7�4
-�*
 �
inputs���������d
p

 
� "�����������
G__inference_sequential_2_layer_call_and_return_conditional_losses_52657uTUVWB�?
8�5
+�(
dense_8_input���������d
p 

 
� ")�&
�
0���������d
� �
G__inference_sequential_2_layer_call_and_return_conditional_losses_52671uTUVWB�?
8�5
+�(
dense_8_input���������d
p

 
� ")�&
�
0���������d
� �
G__inference_sequential_2_layer_call_and_return_conditional_losses_54656nTUVW;�8
1�.
$�!
inputs���������d
p 

 
� ")�&
�
0���������d
� �
G__inference_sequential_2_layer_call_and_return_conditional_losses_54713nTUVW;�8
1�.
$�!
inputs���������d
p

 
� ")�&
�
0���������d
� �
,__inference_sequential_2_layer_call_fn_52570hTUVWB�?
8�5
+�(
dense_8_input���������d
p 

 
� "����������d�
,__inference_sequential_2_layer_call_fn_52643hTUVWB�?
8�5
+�(
dense_8_input���������d
p

 
� "����������d�
,__inference_sequential_2_layer_call_fn_54586aTUVW;�8
1�.
$�!
inputs���������d
p 

 
� "����������d�
,__inference_sequential_2_layer_call_fn_54599aTUVW;�8
1�.
$�!
inputs���������d
p

 
� "����������d�
#__inference_signature_wrapper_53639�KJLMNOPQRSXYTUVWZ[9:HI;�8
� 
1�.
,
input_3!�
input_3���������d"3�0
.
dense_11"�
dense_11����������
Y__inference_token_and_position_embedding_2_layer_call_and_return_conditional_losses_54127[KJ*�'
 �
�
x���������d
� ")�&
�
0���������d
� �
>__inference_token_and_position_embedding_2_layer_call_fn_54103NKJ*�'
 �
�
x���������d
� "����������d�
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54328vLMNOPQRSXYTUVWZ[7�4
-�*
$�!
inputs���������d
p 
� ")�&
�
0���������d
� �
N__inference_transformer_block_2_layer_call_and_return_conditional_losses_54468vLMNOPQRSXYTUVWZ[7�4
-�*
$�!
inputs���������d
p
� ")�&
�
0���������d
� �
3__inference_transformer_block_2_layer_call_fn_54164iLMNOPQRSXYTUVWZ[7�4
-�*
$�!
inputs���������d
p 
� "����������d�
3__inference_transformer_block_2_layer_call_fn_54201iLMNOPQRSXYTUVWZ[7�4
-�*
$�!
inputs���������d
p
� "����������d
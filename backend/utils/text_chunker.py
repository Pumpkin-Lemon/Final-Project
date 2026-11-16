def chunk_text(text,chunk_size=1800,overlap=200):
 if chunk_size<=overlap:raise ValueError("chunk_size ต้องมากกว่า overlap")
 text=" ".join(text.split());out=[];start=0
 while start<len(text):
  end=min(start+chunk_size,len(text));out.append(text[start:end])
  if end==len(text):break
  start=end-overlap
 return out

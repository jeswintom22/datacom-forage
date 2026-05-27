import React, {useEffect, useState} from 'react'

const API = 'http://127.0.0.1:5000/api'

export default function App(){
  const [feed, setFeed] = useState([])
  const [sender, setSender] = useState('alice@example.com')
  const [recipient, setRecipient] = useState('carol@example.com')
  const [message, setMessage] = useState('Great work!')

  useEffect(()=>{loadFeed()}, [])
  async function loadFeed(){
    const r = await fetch(API + '/kudos')
    const data = await r.json()
    setFeed(data)
  }
  async function submit(e){
    e.preventDefault()
    const body = {sender_email: sender, recipient_email: recipient, message}
    const r = await fetch(API + '/kudos', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
    if(r.status===201){
      setMessage('')
      loadFeed()
    } else {
      const err = await r.json()
      alert(err.error || 'Failed')
    }
  }
  return (
    <div style={{maxWidth:800,margin:'2rem auto',fontFamily:'Arial'}}>
      <h1>Kudos</h1>
      <form onSubmit={submit} style={{marginBottom:20}}>
        <div><label>Sender: <input value={sender} onChange={e=>setSender(e.target.value)} /></label></div>
        <div><label>Recipient: <input value={recipient} onChange={e=>setRecipient(e.target.value)} /></label></div>
        <div><textarea value={message} onChange={e=>setMessage(e.target.value)} rows={4} style={{width:'100%'}} maxLength={500} /></div>
        <button type="submit">Send</button>
      </form>
      <h2>Recent</h2>
      {feed.map(k=> (
        <div key={k.id} style={{border:'1px solid #ddd',padding:12,marginBottom:8,borderRadius:6}}>
          <strong>{k.sender_name}</strong> → <strong>{k.recipient_name}</strong>
          <div style={{marginTop:6}}>{k.message}</div>
          <small>{k.created_at}</small>
        </div>
      ))}
    </div>
  )
}

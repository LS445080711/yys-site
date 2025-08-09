
import { useState } from 'react'
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function TeamPage(){
  const [token,setToken] = useState('')
  const [title,setTitle] = useState('我的阵容')
  const [author,setAuthor] = useState('player')
  const [shikiJson,setShikiJson] = useState('[{"position":1,"id":1,"yuhun":"破势 4件"}]')
  const [msg,setMsg] = useState('')
  async function login(){ // demo login: register if needed then login
    const username = prompt('用户名 (测试用)')
    const password = prompt('密码')
    if(!username || !password) return
    await fetch(API + '/api/auth/register', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({username,password})}).catch(()=>{})
    const r = await fetch(API + '/api/auth/login', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({username,password})})
    const data = await r.json()
    if(data.access_token){ setToken(data.access_token); setMsg('登录成功') }
  }
  async function submitTeam(){
    if(!token){ setMsg('请先登录'); return }
    try{
      const body = { title, author, shikigami_order: JSON.parse(shikiJson), strategy: '' }
      const r = await fetch(API + '/api/teams', {method:'POST', headers:{'content-type':'application/json', 'authorization': 'Bearer ' + token}, body: JSON.stringify(body)})
      const d = await r.json()
      setMsg(JSON.stringify(d))
    }catch(e){ setMsg('提交失败: '+e.message) }
  }
  return (
    <div style={{padding:20,fontFamily:'sans-serif'}}>
      <h1>投稿阵容（示例）</h1>
      <p><button onClick={login}>登录/注册（演示）</button></p>
      <p>题目：<input value={title} onChange={e=>setTitle(e.target.value)}/></p>
      <p>作者：<input value={author} onChange={e=>setAuthor(e.target.value)}/></p>
      <p>shikigami_order (JSON)：<br/><textarea rows={6} cols={60} value={shikiJson} onChange={e=>setShikiJson(e.target.value)} /></p>
      <p><button onClick={submitTeam}>提交阵容</button></p>
      <p>{msg}</p>
    </div>
  )
}

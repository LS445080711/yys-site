import useSWR from 'swr'
import { useRouter } from 'next/router'
const fetcher = (url) => fetch(url).then(r=>r.json())

export default function ShikiPage(){
  const router = useRouter()
  const { slug } = router.query
  const {data, error} = useSWR(slug ? `http://localhost:8000/api/shikigami/${slug}` : null, fetcher)
  if(error) return <div>加载失败</div>
  if(!data) return <div>加载中...</div>
  const s = data
  return (
    <div style={{padding:20,fontFamily:'sans-serif'}}>
      <h1>{s.name} <small>({s.rarity}★)</small></h1>
      <img src={s.avatar_url} style={{width:120}}/>
      <h3>定位：{s.role}</h3>
      <h3>技能</h3>
      <pre>{JSON.stringify(s.skills,null,2)}</pre>
      <h3>推荐御魂</h3>
      <ul>{(s.recommended_souls||[]).map((r,i)=><li key={i}>{r}</li>)}</ul>
    </div>
  )
}
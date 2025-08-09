import Link from 'next/link'
import useSWR from 'swr'
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const fetcher = (url) => fetch(url).then(r=>r.json())

export default function Home(){
  const {data, error} = useSWR(API + '/api/shikigami', fetcher)
  if(error) return <div>加载失败（请确保后端在 {API} 运行）</div>
  if(!data) return <div>加载中...</div>
  return (
    <div style={{padding:20,fontFamily:'sans-serif'}}>
      <h1>阴阳师 式神数据库（示例）</h1>
      <ul>
        {data.map(s => (
          <li key={s.id} style={{marginBottom:8}}>
            <img src={s.avatar_url} alt="" style={{width:48,height:48,verticalAlign:'middle'}}/>
            <Link href={'/shikigami/'+s.slug}><a style={{marginLeft:10}}>{s.name} ({s.rarity}★) - {s.role}</a></Link>
          </li>
        ))}
      </ul>
    </div>
  )
}

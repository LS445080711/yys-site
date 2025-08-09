import Link from 'next/link'
export default function Page() {
  return (
    <main style={{padding:20,fontFamily:'sans-serif'}}>
      <h1>阴阳师（App Router）示例首页</h1>
      <p><Link href='/shikigami/ibuki'>示例：茨木童子</Link></p>
    </main>
  )
}

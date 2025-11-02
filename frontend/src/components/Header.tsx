export function Header() {
  return (
    <header className="glass px-4 py-3 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-semibold bg-[image:var(--grad-primary)] bg-clip-text text-transparent">Erik’s Super Compare</h1>
        <p className="text-sm text-white/60">Redlines so good, even Litera blushes.</p>
      </div>
      <div className="hidden sm:block text-xs text-white/50">v1</div>
    </header>
  )
}



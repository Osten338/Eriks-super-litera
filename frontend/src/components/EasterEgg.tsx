type Props = {
  total: number
}

export function EasterEgg({ total }: Props) {
  if (total === 0) {
    return (
      <div className="text-center p-8">
        <img src="/images/judge-dredd.png" alt="Approved" className="mx-auto h-40" />
        <div className="mt-2 font-medium">Approved.</div>
      </div>
    )
  }
  if (total > 30) {
    return (
      <div className="text-center p-8">
        <img src="/images/christmas-tree.gif" alt="Christmas tree" className="mx-auto h-40" />
        <div className="mt-2 font-medium">Too many changes – it’s a Christmas tree!</div>
      </div>
    )
  }
  return null
}



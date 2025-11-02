import SidebarSettings from './organisms/SidebarSettings'

type Props = {
  includeFormatting: boolean
  setIncludeFormatting: (v: boolean) => void
  ocr: boolean
  setOcr: (v: boolean) => void
}

export function SettingsPane({ includeFormatting, setIncludeFormatting, ocr, setOcr }: Props) {
  return (
    <SidebarSettings
      includeFormatting={includeFormatting}
      setIncludeFormatting={setIncludeFormatting}
      ocr={ocr}
      setOcr={setOcr}
    />
  )
}



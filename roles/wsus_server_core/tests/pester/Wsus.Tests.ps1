Describe "WSUS Installation" {

    Context "Services" {
        It "WsusService service should be running" {
            $service = Get-Service -Name "WsusService" -ErrorAction SilentlyContinue
            $service.Status | Should -Be "Running"
        }
        
        It "Service startup type should be Automatic" {
            $service = Get-Service -Name "WsusService" -ErrorAction SilentlyContinue
            $service.StartType | Should -Be "Automatic"
        }
    }

    Context "Files" {
        
        It "Installation directory should exist" {
            $installPath = "C:\Program Files\Update Services"
            Test-Path $installPath | Should -Be $true
        }
    }
    
    Context "Registry" {
        It "Specified registry key should exist" {
            Test-Path "HKLM:\SOFTWARE\Microsoft\Update Services\Server" | Should -Be $true
        }
    }
}

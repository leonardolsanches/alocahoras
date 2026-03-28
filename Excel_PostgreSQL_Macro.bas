Sub ConectarPostgreSQL()
'
' Macro para conectar Excel ao PostgreSQL e carregar dados completos
' Execute este macro no Excel com a planilha de dados aberta
'
    Dim conn As Object
    Dim rs As Object
    Dim sql As String
    Dim connectionString As String
    
    ' String de conexão PostgreSQL
    connectionString = "Provider=PostgreSQL OLE DB Provider;Data Source=ep-steep-math-a6gyny5t.us-west-2.aws.neon.tech;Initial Catalog=neondb;User Id=neondb_owner;Password=npg_rO3V1ilKuMUh;Port=5432;SSL Mode=require;"
    
    ' Criar objetos de conexão
    Set conn = CreateObject("ADODB.Connection")
    Set rs = CreateObject("ADODB.Recordset")
    
    On Error GoTo ErrorHandler
    
    ' Conectar ao banco
    Application.StatusBar = "Conectando ao PostgreSQL..."
    conn.Open connectionString
    
    MsgBox "✅ Conectado com sucesso ao PostgreSQL!" & vbCrLf & _
           "Agora você pode executar as próximas macros para carregar dados.", vbInformation
    
    ' Fechar conexão
    conn.Close
    Set conn = Nothing
    Set rs = Nothing
    Application.StatusBar = False
    
    Exit Sub
    
ErrorHandler:
    MsgBox "❌ Erro de conexão: " & Err.Description & vbCrLf & vbCrLf & _
           "Verifique se o driver PostgreSQL ODBC está instalado.", vbCritical
    Application.StatusBar = False
    If Not conn Is Nothing Then
        If conn.State = 1 Then conn.Close
    End If
End Sub

Sub CarregarDadosCompletos()
'
' Carrega todos os 828 registros da planilha atual para o PostgreSQL
'
    Dim conn As Object
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim colaborador As String
    Dim projeto As String
    Dim atividade As String
    Dim tipo As String
    Dim mes As String
    Dim horas As String
    Dim sql As String
    Dim connectionString As String
    Dim progressCount As Long
    
    ' String de conexão
    connectionString = "Provider=PostgreSQL OLE DB Provider;Data Source=ep-steep-math-a6gyny5t.us-west-2.aws.neon.tech;Initial Catalog=neondb;User Id=neondb_owner;Password=npg_rO3V1ilKuMUh;Port=5432;SSL Mode=require;"
    
    Set ws = ActiveSheet
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    Set conn = CreateObject("ADODB.Connection")
    
    On Error GoTo ErrorHandler
    
    ' Conectar
    conn.Open connectionString
    
    ' Limpar dados antigos
    Application.StatusBar = "Limpando dados antigos..."
    conn.Execute "DELETE FROM allocations;"
    conn.Execute "DELETE FROM collaborators WHERE id > 0;"
    conn.Execute "DELETE FROM projects WHERE id > 0;"
    conn.Execute "DELETE FROM activities WHERE id > 0;"
    conn.Execute "DELETE FROM allocation_types WHERE id > 0;"
    
    ' Arrays para IDs únicos
    Dim colaboradores As New Collection
    Dim projetos As New Collection
    Dim atividades As New Collection
    Dim tipos As New Collection
    
    ' Coletar dados únicos primeiro
    Application.StatusBar = "Coletando dados únicos..."
    For i = 2 To lastRow ' Começar na linha 2 (pular cabeçalho)
        
        colaborador = Trim(ws.Cells(i, 1).Value) ' Coluna A - COLABORADORES
        projeto = Trim(ws.Cells(i, 3).Value)     ' Coluna C - PROJETOS  
        atividade = Trim(ws.Cells(i, 4).Value)   ' Coluna D - ATIVIDADES
        tipo = Trim(ws.Cells(i, 5).Value)        ' Coluna E - TIPO ALOCACAO
        
        ' Adicionar às coleções se não existir
        On Error Resume Next
        colaboradores.Add colaborador, colaborador
        projetos.Add projeto, projeto
        atividades.Add atividade, atividade
        tipos.Add tipo, tipo
        On Error GoTo ErrorHandler
        
    Next i
    
    ' Inserir colaboradores únicos
    Application.StatusBar = "Inserindo " & colaboradores.Count & " colaboradores..."
    For i = 1 To colaboradores.Count
        sql = "INSERT INTO collaborators (id, full_name, department, manager_id, is_manager) VALUES (" & _
              i & ", '" & Replace(colaboradores(i), "'", "''") & "', 'TI', 'ALINE JULIANA LOPES', false);"
        conn.Execute sql
    Next i
    
    ' Inserir projetos únicos
    Application.StatusBar = "Inserindo " & projetos.Count & " projetos..."
    For i = 1 To projetos.Count
        sql = "INSERT INTO projects (id, project_code, project_name, is_active) VALUES (" & _
              i & ", 'PROJ" & Format(i, "000") & "', '" & Replace(projetos(i), "'", "''") & "', true);"
        conn.Execute sql
    Next i
    
    ' Inserir atividades únicas
    Application.StatusBar = "Inserindo " & atividades.Count & " atividades..."
    For i = 1 To atividades.Count
        sql = "INSERT INTO activities (id, activity_code, activity_name, is_active) VALUES (" & _
              i & ", 'ACT" & Format(i, "000") & "', '" & Replace(atividades(i), "'", "''") & "', true);"
        conn.Execute sql
    Next i
    
    ' Inserir tipos únicos
    Application.StatusBar = "Inserindo " & tipos.Count & " tipos..."
    For i = 1 To tipos.Count
        sql = "INSERT INTO allocation_types (id, type_code, type_name, is_active) VALUES (" & _
              i & ", 'TIPO" & Format(i, "000") & "', '" & Replace(tipos(i), "'", "''") & "', true);"
        conn.Execute sql
    Next i
    
    ' Inserir alocações para cada mês
    Application.StatusBar = "Inserindo alocações..."
    progressCount = 0
    
    For i = 2 To lastRow
        colaborador = Trim(ws.Cells(i, 1).Value)
        projeto = Trim(ws.Cells(i, 3).Value)
        atividade = Trim(ws.Cells(i, 4).Value)
        tipo = Trim(ws.Cells(i, 5).Value)
        
        ' Encontrar IDs
        Dim colabId, projId, ativId, tipoId As Long
        For j = 1 To colaboradores.Count
            If colaboradores(j) = colaborador Then colabId = j: Exit For
        Next j
        For j = 1 To projetos.Count
            If projetos(j) = projeto Then projId = j: Exit For
        Next j
        For j = 1 To atividades.Count
            If atividades(j) = atividade Then ativId = j: Exit For
        Next j
        For j = 1 To tipos.Count
            If tipos(j) = tipo Then tipoId = j: Exit For
        Next j
        
        ' Para cada mês (colunas F a Q = meses JAN a DEZ)
        For mesCol = 6 To 17 ' Colunas F-Q
            horas = Trim(ws.Cells(i, mesCol).Value)
            If horas <> "" And horas <> "-" And horas <> "0" Then
                
                Dim mesNum As Long
                mesNum = mesCol - 5 ' F=1 (Jan), G=2 (Fev), etc.
                
                ' Limpar valor de horas
                horas = Replace(horas, "h", "")
                horas = Replace(horas, ",", ".")
                If IsNumeric(horas) Then
                    
                    sql = "INSERT INTO allocations (collaborator_id, project_id, activity_id, allocation_type_id, " & _
                          "allocation_date, hours, percentage, status) VALUES (" & _
                          colabId & ", " & projId & ", " & ativId & ", " & tipoId & ", " & _
                          "'2025-" & Format(mesNum, "00") & "-01', " & horas & ", 100.0, 'pendente');"
                    
                    conn.Execute sql
                    progressCount = progressCount + 1
                    
                    ' Atualizar progresso a cada 50 registros
                    If progressCount Mod 50 = 0 Then
                        Application.StatusBar = "Inseridas " & progressCount & " alocações..."
                    End If
                    
                End If
            End If
        Next mesCol
    Next i
    
    ' Finalizar
    conn.Close
    Set conn = Nothing
    Application.StatusBar = False
    
    MsgBox "🎉 SUCESSO! " & vbCrLf & vbCrLf & _
           "✅ " & colaboradores.Count & " colaboradores carregados" & vbCrLf & _
           "✅ " & projetos.Count & " projetos carregados" & vbCrLf & _
           "✅ " & atividades.Count & " atividades carregadas" & vbCrLf & _
           "✅ " & tipos.Count & " tipos carregados" & vbCrLf & _
           "✅ " & progressCount & " alocações inseridas" & vbCrLf & vbCrLf & _
           "Dados completos carregados no PostgreSQL!", vbInformation
    
    Exit Sub
    
ErrorHandler:
    MsgBox "❌ Erro: " & Err.Description, vbCritical
    Application.StatusBar = False
    If Not conn Is Nothing Then
        If conn.State = 1 Then conn.Close
    End If
End Sub

Sub VerificarProgresso()
'
' Verifica quantos registros foram carregados no banco
'
    Dim conn As Object
    Dim rs As Object
    Dim connectionString As String
    
    connectionString = "Provider=PostgreSQL OLE DB Provider;Data Source=ep-steep-math-a6gyny5t.us-west-2.aws.neon.tech;Initial Catalog=neondb;User Id=neondb_owner;Password=npg_rO3V1ilKuMUh;Port=5432;SSL Mode=require;"
    
    Set conn = CreateObject("ADODB.Connection")
    Set rs = CreateObject("ADODB.Recordset")
    
    On Error GoTo ErrorHandler
    
    conn.Open connectionString
    
    ' Verificar contagens
    rs.Open "SELECT COUNT(*) FROM allocations", conn
    Dim totalAloc As Long
    totalAloc = rs.Fields(0).Value
    rs.Close
    
    rs.Open "SELECT COUNT(DISTINCT collaborator_id) FROM allocations", conn
    Dim totalColab As Long
    totalColab = rs.Fields(0).Value
    rs.Close
    
    rs.Open "SELECT COUNT(*) FROM projects", conn
    Dim totalProj As Long
    totalProj = rs.Fields(0).Value
    rs.Close
    
    Dim progresso As Double
    progresso = (totalAloc / 828) * 100
    
    MsgBox "📊 PROGRESSO ATUAL:" & vbCrLf & vbCrLf & _
           "Alocações: " & totalAloc & " / 828 (" & Format(progresso, "0.0") & "%)" & vbCrLf & _
           "Colaboradores: " & totalColab & vbCrLf & _
           "Projetos: " & totalProj & vbCrLf & vbCrLf & _
           "Meta: 100% dos dados autênticos", vbInformation
    
    conn.Close
    Exit Sub
    
ErrorHandler:
    MsgBox "❌ Erro: " & Err.Description, vbCritical
    If Not conn Is Nothing Then
        If conn.State = 1 Then conn.Close
    End If
End Sub
Sub ConectarPostgreSQLODBC()
'
' Versão alternativa usando ODBC - mais compatível
'
    Dim conn As Object
    Dim connectionString As String
    
    ' String ODBC para PostgreSQL
    connectionString = "DRIVER={PostgreSQL UNICODE};" & _
                      "SERVER=ep-steep-math-a6gyny5t.us-west-2.aws.neon.tech;" & _
                      "PORT=5432;" & _
                      "DATABASE=neondb;" & _
                      "UID=neondb_owner;" & _
                      "PWD=npg_rO3V1ilKuMUh;" & _
                      "SSLMode=require;"
    
    Set conn = CreateObject("ADODB.Connection")
    
    On Error GoTo ErrorHandler
    
    Application.StatusBar = "Testando conexão ODBC..."
    conn.Open connectionString
    
    MsgBox "✅ Conexão ODBC estabelecida com sucesso!" & vbCrLf & _
           "Agora execute CarregarDadosViaODBC() para carregar os dados.", vbInformation
    
    conn.Close
    Application.StatusBar = False
    Exit Sub
    
ErrorHandler:
    MsgBox "❌ Driver PostgreSQL ODBC não encontrado!" & vbCrLf & vbCrLf & _
           "SOLUÇÃO ALTERNATIVA:" & vbCrLf & _
           "1. Use CarregarViaExcel() em vez disso" & vbCrLf & _
           "2. Ou baixe o driver em: https://www.postgresql.org/ftp/odbc/versions/msi/", vbCritical
    Application.StatusBar = False
End Sub

Sub CarregarViaExcel()
'
' Carrega dados sem conectar diretamente - gera script SQL
'
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim script As String
    Dim newWs As Worksheet
    
    Set ws = ActiveSheet
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    ' Criar nova aba para o script SQL
    Set newWs = Worksheets.Add
    newWs.Name = "Script_SQL_" & Format(Now, "hhmmss")
    
    script = "-- SCRIPT GERADO AUTOMATICAMENTE PARA CARREGAR " & (lastRow - 1) & " REGISTROS" & vbCrLf & vbCrLf
    script = script & "-- 1. LIMPAR DADOS ANTIGOS" & vbCrLf
    script = script & "DELETE FROM allocations;" & vbCrLf
    script = script & "DELETE FROM collaborators WHERE id > 0;" & vbCrLf
    script = script & "DELETE FROM projects WHERE id > 0;" & vbCrLf
    script = script & "DELETE FROM activities WHERE id > 0;" & vbCrLf
    script = script & "DELETE FROM allocation_types WHERE id > 0;" & vbCrLf & vbCrLf
    
    ' Coletar dados únicos
    Dim colaboradores As New Collection
    Dim projetos As New Collection
    Dim atividades As New Collection
    Dim tipos As New Collection
    
    Application.StatusBar = "Processando " & (lastRow - 1) & " registros..."
    
    ' Primeira passada - coletar únicos
    For i = 2 To lastRow
        On Error Resume Next
        colaboradores.Add ws.Cells(i, 1).Value, CStr(ws.Cells(i, 1).Value)
        projetos.Add ws.Cells(i, 3).Value, CStr(ws.Cells(i, 3).Value)
        atividades.Add ws.Cells(i, 4).Value, CStr(ws.Cells(i, 4).Value)
        tipos.Add ws.Cells(i, 5).Value, CStr(ws.Cells(i, 5).Value)
        On Error GoTo 0
    Next i
    
    ' Gerar INSERTs para colaboradores
    script = script & "-- 2. INSERIR " & colaboradores.Count & " COLABORADORES" & vbCrLf
    For i = 1 To colaboradores.Count
        script = script & "INSERT INTO collaborators (id, full_name, department, manager_id, is_manager) VALUES " & _
                 "(" & i & ", '" & Replace(colaboradores(i), "'", "''") & "', 'TI', 'ALINE JULIANA LOPES', false);" & vbCrLf
    Next i
    
    script = script & vbCrLf & "-- 3. INSERIR " & projetos.Count & " PROJETOS" & vbCrLf
    For i = 1 To projetos.Count
        script = script & "INSERT INTO projects (id, project_code, project_name, is_active) VALUES " & _
                 "(" & i & ", 'PROJ" & Format(i, "000") & "', '" & Replace(projetos(i), "'", "''") & "', true);" & vbCrLf
    Next i
    
    script = script & vbCrLf & "-- 4. INSERIR " & atividades.Count & " ATIVIDADES" & vbCrLf
    For i = 1 To atividades.Count
        script = script & "INSERT INTO activities (id, activity_code, activity_name, is_active) VALUES " & _
                 "(" & i & ", 'ACT" & Format(i, "000") & "', '" & Replace(atividades(i), "'", "''") & "', true);" & vbCrLf
    Next i
    
    script = script & vbCrLf & "-- 5. INSERIR " & tipos.Count & " TIPOS" & vbCrLf
    For i = 1 To tipos.Count
        script = script & "INSERT INTO allocation_types (id, type_code, type_name, is_active) VALUES " & _
                 "(" & i & ", 'TIPO" & Format(i, "000") & "', '" & Replace(tipos(i), "'", "''") & "', true);" & vbCrLf
    Next i
    
    script = script & vbCrLf & "-- 6. INSERIR ALOCAÇÕES (TODAS AS COMBINAÇÕES COLABORADOR+MÊS)" & vbCrLf
    
    Dim alocCount As Long
    alocCount = 0
    
    ' Segunda passada - gerar alocações
    For i = 2 To lastRow
        Dim colaborador, projeto, atividade, tipo As String
        colaborador = ws.Cells(i, 1).Value
        projeto = ws.Cells(i, 3).Value
        atividade = ws.Cells(i, 4).Value
        tipo = ws.Cells(i, 5).Value
        
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
        
        ' Para cada mês (colunas F a Q)
        For mesCol = 6 To 17
            Dim horas As String
            horas = Trim(ws.Cells(i, mesCol).Value)
            
            If horas <> "" And horas <> "-" And horas <> "0" Then
                horas = Replace(horas, "h", "")
                horas = Replace(horas, ",", ".")
                
                If IsNumeric(horas) Then
                    Dim mesNum As Long
                    mesNum = mesCol - 5
                    
                    script = script & "INSERT INTO allocations (collaborator_id, project_id, activity_id, allocation_type_id, allocation_date, hours, percentage, status) VALUES " & _
                             "(" & colabId & ", " & projId & ", " & ativId & ", " & tipoId & ", '2025-" & Format(mesNum, "00") & "-01', " & horas & ", 100.0, 'pendente');" & vbCrLf
                    
                    alocCount = alocCount + 1
                End If
            End If
        Next mesCol
        
        ' Atualizar progresso
        If i Mod 50 = 0 Then
            Application.StatusBar = "Processando linha " & i & " de " & lastRow & "..."
        End If
    Next i
    
    script = script & vbCrLf & "-- RESUMO: " & alocCount & " ALOCAÇÕES INSERIDAS" & vbCrLf
    script = script & "SELECT COUNT(*) as total_alocacoes FROM allocations;" & vbCrLf
    script = script & "SELECT COUNT(DISTINCT collaborator_id) as total_colaboradores FROM allocations;"
    
    ' Escrever script na nova aba
    newWs.Cells(1, 1).Value = script
    newWs.Columns(1).ColumnWidth = 100
    newWs.Rows(1).WrapText = True
    
    Application.StatusBar = False
    
    MsgBox "✅ SCRIPT SQL GERADO COM SUCESSO!" & vbCrLf & vbCrLf & _
           "📊 ESTATÍSTICAS:" & vbCrLf & _
           "• " & colaboradores.Count & " colaboradores únicos" & vbCrLf & _
           "• " & projetos.Count & " projetos únicos" & vbCrLf & _
           "• " & atividades.Count & " atividades únicas" & vbCrLf & _
           "• " & tipos.Count & " tipos únicos" & vbCrLf & _
           "• " & alocCount & " alocações geradas" & vbCrLf & vbCrLf & _
           "PRÓXIMO PASSO:" & vbCrLf & _
           "1. Copie o SQL da aba '" & newWs.Name & "'" & vbCrLf & _
           "2. Execute no PostgreSQL para carregar dados completos", vbInformation
    
    ' Ir para a nova aba
    newWs.Activate
End Sub

Sub GerarArquivoSQL()
'
' Salva o script SQL em arquivo .sql
'
    Dim ws As Worksheet
    Dim script As String
    Dim filePath As String
    Dim fileNum As Integer
    
    Set ws = ActiveSheet
    script = ws.Cells(1, 1).Value
    
    ' Definir caminho do arquivo
    filePath = ThisWorkbook.Path & "\dados_completos_postgresql.sql"
    
    ' Escrever arquivo
    fileNum = FreeFile
    Open filePath For Output As fileNum
    Print #fileNum, script
    Close fileNum
    
    MsgBox "✅ Arquivo SQL salvo em:" & vbCrLf & filePath & vbCrLf & vbCrLf & _
           "Execute este arquivo no PostgreSQL para carregar todos os dados!", vbInformation
End Sub
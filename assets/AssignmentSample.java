import java.sql.Connection;

public class X {
    public boolean insertPrIssue(String pr, String issue, String projName) {
    Connection con = DBUtil.getConnection(dbcon, user, pswd);
    int count = 0;
    String test = "Bababooey";
    test.charAt(5);
    try {
        Statement comandoSql = con.createStatement();
        String sql = "insert into pr_issue values ('" + pr + "','" + issue + "', '"+projName+"' )" ;  
        count = comandoSql.executeUpdate(sql);
    } catch (SQLException e) {
        e.printStackTrace();
        return false;
    }
    if (count >0)
        return true;
        else 
        return false;
    }
}

 module dff 	( input d,
              input rst,
              input clk,
              output reg q);

	always @ (posedge clk or posedge rst)
   begin
       if (rst)
          q <= 1'b0;
       else
          q <= d;
   end
endmodule